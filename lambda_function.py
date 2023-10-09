import json
import time
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.sdk.async_api import CdcAsyncApi
from crypto_dot_com.secret import API_KEY, SECRET_KEY
from crypto_dot_com.utils.ascii_chart import gen_ascii_plot
from crypto_dot_com.utils.ticker import get_yfinance_ticker_price
from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext


def lambda_handler(event=None, context=None):
    start_time = time.time()
    api = CdcAsyncApi(api_key=API_KEY, secret_key=SECRET_KEY)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    (
        user_balance_history,
        user_balance,
        tickers,
        open_orders,
        sgd_usd,
    ) = loop.run_until_complete(
        asyncio.gather(
            api.get_user_balance_history(timeframe="H1", limit=40),
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
    position_balances = list(filter(lambda p: p["notional"] > 10, position_balances))

    m = {"5m": 5, "1h": 60, "6h": 60 * 6, "24h": 60 * 24}

    async def update_price_changes(position_balance: dict):
        ccy = position_balance["ccy"]
        ticker = tickers_map.get(f"{ccy}_USDT") or tickers_map.get(f"{ccy}_USD")
        if ticker:
            price, instrument_name = get_spot_price(ccy)
            candlesticks = await api.get_candlestick(
                instrument_name, timeframe="5m", count=300
            )
            candlesticks.sort(reverse=True, key=lambda d: d["t"])
            base_interval = 5
            for key, interval in m.items():
                open_price = float(candlesticks[interval // base_interval]["o"])
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

    bal_df = pd.DataFrame(position_balances)
    bal_df = bal_df.sort_values(by=["notional"], ascending=False)
    bal_df["notional"] = bal_df["notional"].map(lambda v: f"${v:,.2f}")
    bal_df = bal_df[["ccy", "notional", *m.keys()]]
    bal_df = bal_df.replace(np.nan, "")

    user_balance_history.sort(key=lambda d: d["t"])
    points = list(map(lambda d: float(d["c"]), user_balance_history))
    points.append(total_cash_balance)
    chart = gen_ascii_plot(points=points[-33:])
    balances = pd.Series(
        data={
            "Exch Balance:": f"${total_cash_balance:,.2f}",
            " Sgd Balance:": f"${sgd_cash_balance:,.2f}",
        }
    ).to_string()

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)
    bal_table = bal_df.to_string(index=False).replace("_", "-")

    end_time = time.time()
    duration = f"[Finished in {end_time - start_time:,.3f}s]"

    delimiter = "\n\n"
    msg = f"{delimiter.join([dt, bal_table, balances, chart])}"
    if orders_table:
        msg += delimiter + orders_table
    msg = "```" + msg + delimiter + duration + "```"

    resp = telegram_bot_sendtext(msg)

    return {"statusCode": 200, "body": json.dumps(resp)}


if __name__ == "__main__":
    lambda_handler()
