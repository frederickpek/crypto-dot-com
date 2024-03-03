import json
import time
import asyncio
import traceback
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.sdk.async_api import CdcAsyncApi
from crypto_dot_com.secret import (
    CDC_API_KEY_ROD,
    CDC_SECRET_KEY_ROD,
    SPREADSHEET_ID,
    TELE_BOT_CHAT_ID_ROD,
)

from crypto_dot_com.utils.ascii_chart import gen_ascii_plot
from crypto_dot_com.utils.ticker import get_yfinance_ticker_price
from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext
from crypto_dot_com.utils.GoogleSheetsClient import GoogleSheetsClient

GSDB_CDC_EXCHANGE_BALANCE_CELL = "B5"


def format_qty(x: float) -> str:
    x0 = x
    try:
        if x < 1000:
            return f"{x:.2f}"
        suffixes = ["", "k", "M", "B", "T"]
        for i in range(len(suffixes)):
            if x >= 1000:
                x /= 1000
                continue
            x: str = str(float(x)) + "000"
            x = x[:3] if x.find(".") == 3 else x[:4]
            return x + suffixes[i]
        return ">1e15"  # can never be <-1e15
    except:
        pass
    return f"{x0:,}"


def format_price(x: float) -> str:
    if x > 0.999:
        return f"{x:,.2f}"
    return f"{x:.2e}"


def main():
    start_time = time.time()
    api = CdcAsyncApi(api_key=CDC_API_KEY_ROD, secret_key=CDC_SECRET_KEY_ROD)
    gsdb = GoogleSheetsClient(
        "./crypto_dot_com/credentials.json", spreadsheet_id=SPREADSHEET_ID
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    (
        user_balance,
        tickers,
        open_orders,
        sgd_usd,
    ) = loop.run_until_complete(
        asyncio.gather(
            api.get_user_balance(),
            api.get_tickers(),
            api.get_open_orders(),
            get_yfinance_ticker_price(ticker="SGDUSD=X"),
        )
    )

    tickers_map = {ticker["i"]: ticker for ticker in tickers}
    total_cash_balance = float(user_balance["total_cash_balance"])
    position_balances = user_balance["position_balances"]

    def get_spot_price(ccy):
        ticker = (
            tickers_map.get(f"{ccy}_USDT")
            or tickers_map.get(f"{ccy}_USD")
            or tickers_map.get(ccy)
        )
        price, instrument_name = 1.0, "USD"
        if ticker:
            instrument_name = ticker["i"]
            bid, ask = float(ticker["b"]), float(ticker["k"])
            price = (bid + ask) / 2
        return price, instrument_name

    # derive total notional value
    position_balances = list(
        map(
            lambda p: {
                **p,
                "notional": float(p["quantity"])
                * get_spot_price(p["instrument_name"])[0],
            },
            position_balances,
        )
    )

    # filter low balance coins
    position_balances = list(filter(lambda p: p["notional"] > 3, position_balances))

    ccy_candlesticks = {}
    m = {"5m": 5, "1h": 60, "6h": 60 * 6, "24h": 60 * 24}

    async def update_price_changes(position_balance: dict):
        ccy = position_balance["ccy"]
        ticker = tickers_map.get(f"{ccy}_USDT") or tickers_map.get(f"{ccy}_USD")
        price, instrument_name = get_spot_price(ccy)
        position_balance["price"] = price
        portfolio_percentage = position_balance["notional"] / total_cash_balance * 100
        position_balance["pct"] = f"{portfolio_percentage:,.2f}%"
        if not ticker:
            return
        candlesticks = await api.get_candlestick(
            instrument_name, timeframe="5m", count=300
        )
        ccy_candlesticks[ccy] = candlesticks
        candlesticks.sort(reverse=True, key=lambda d: d["t"])
        base_interval = 5
        for key, interval in m.items():
            index = interval // base_interval
            index = index if index < len(candlesticks) else -1
            open_price = float(candlesticks[index]["o"])
            percentage = (price - open_price) / price * 100
            position_balance[key] = f"{percentage:,.1f}"

    loop.run_until_complete(
        asyncio.gather(
            *[
                update_price_changes(position_balance)
                for position_balance in position_balances
            ]
        )
    )

    sgd_cash_balance = total_cash_balance / sgd_usd

    # open orders
    if open_orders:
        orders_df = pd.DataFrame(open_orders)
        orders_df["inst"] = orders_df["instrument_name"]
        orders_df["qty"] = orders_df["quantity"]
        orders_df["limit"] = orders_df["limit_price"].map(float)
        orders_df["price"] = orders_df["instrument_name"].apply(
            lambda i: get_spot_price(i)[0]
        )
        orders_df["limit"] = orders_df["limit"].map(lambda v: f"{v:,.2f}")
        orders_df["price"] = orders_df["price"].map(lambda v: f"{v:,.2f}")
        orders_df = orders_df[["inst", "side", "qty", "limit", "price"]]
        orders_table = "Open Orders\n" + orders_df.to_string(index=False).replace(
            "_", "-"
        )
    else:
        orders_table = None

    # balances breakdown
    bal_df = pd.DataFrame(position_balances)
    bal_df = bal_df.sort_values(by=["notional"], ascending=False)
    bal_df["notional"] = bal_df["notional"].map(lambda v: f"${v:,.2f}")
    bal_df["price"] = bal_df["price"].map(lambda v: f"${v:,.2f}")
    bal_df["qty"] = bal_df["quantity"].map(lambda v: format_qty(float(v)))
    bal_df["ccy"] = bal_df["ccy"].map(lambda v: v[:4])
    bal_df = bal_df[["ccy", "notional", "qty", "pct"]]
    bal_table = bal_df.to_string(index=False)

    # prices
    price_df = pd.DataFrame(position_balances)
    price_df = price_df.dropna()
    price_df = price_df.sort_values(by=["price"])
    price_df["price"] = price_df["price"].map(lambda v: "$" + format_price(v))
    price_df["ccy"] = price_df["ccy"].map(lambda v: v[:4])
    price_df = price_df[["ccy", "price", *m.keys()]]
    price_table = price_df.to_string(index=False)

    # chart
    max_num_points = 32
    ts_now = datetime.now().replace(minute=0, second=0, microsecond=0).timestamp()
    point_now = {str(int(ts_now)): total_cash_balance}
    time_series: dict = json.loads(gsdb.get_cell(GSDB_CDC_EXCHANGE_BALANCE_CELL))
    time_series.update(point_now)
    time_series_list = [(ts, bal) for ts, bal in time_series.items()]
    time_series_list.sort(key=lambda x: x[0])
    time_series_list = time_series_list[-max_num_points:]
    points = list(map(lambda x: x[1], time_series_list))
    chart = gen_ascii_plot(points=points)

    # save data
    series_dict = {ts: bal for ts, bal in time_series_list}
    gsdb.update_cell(GSDB_CDC_EXCHANGE_BALANCE_CELL, json.dumps(series_dict))

    # balances
    balances = pd.Series(
        data={
            "Exch Balance:": f"${total_cash_balance:,.2f}",
            " Sgd Balance:": f"${sgd_cash_balance:,.2f}",
        }
    ).to_string()

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    end_time = time.time()
    duration = f"[Finished in {end_time - start_time:,.3f}s]"

    delimiter = "\n\n"
    msg = f"{delimiter.join([dt, bal_table, balances, chart, price_table])}"
    if orders_table:
        msg += delimiter + orders_table
    msg = "```" + msg + delimiter + duration + "```"

    resp = telegram_bot_sendtext(msg, chat_id=TELE_BOT_CHAT_ID_ROD)

    return {"statusCode": 200, "body": json.dumps(resp)}


def lambda_handler(event=None, context=None):
    try:
        return main()
    except Exception as err:
        err_msg = f"{err}\n{traceback.format_exc()}"
        telegram_bot_sendtext(err_msg, chat_id=TELE_BOT_CHAT_ID_ROD)
    return {"statusCode": 500}


if __name__ == "__main__":
    lambda_handler()
