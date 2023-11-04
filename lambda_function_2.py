import json
import time
import asyncio
import traceback
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from crypto_dot_com.sdk.async_api import CdcAsyncApi
from crypto_dot_com.secret import SUB_ACCT_KEYS
from crypto_dot_com.utils.ticker import get_yfinance_ticker_price
from crypto_dot_com.utils.telegram_bot import telegram_bot_sendtext


def main():
    start_time = time.time()

    apis = {
        acct_id: CdcAsyncApi(api_key=keys["API_KEY"], secret_key=keys["SECRET_KEY"])
        for acct_id, keys in SUB_ACCT_KEYS.items()
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def get_acct_user_balance(acct_id: str, api: CdcAsyncApi):
        user_balance = await api.get_user_balance()
        return acct_id, user_balance

    (
        tickers,
        sgd_usd,
        *acct_balances,
    ) = loop.run_until_complete(
        asyncio.gather(
            list(apis.values())[0].get_tickers(),
            get_yfinance_ticker_price(ticker="SGDUSD=X"),
            *[get_acct_user_balance(acct_id, api) for acct_id, api in apis.items()],
        )
    )

    tickers_map = {ticker["i"]: ticker for ticker in tickers}
    acct_position_balances = [
        (acct_id, user_balance["position_balances"])
        for acct_id, user_balance in acct_balances
    ]

    def get_spot_price(ccy):
        ticker = (
            tickers_map.get(f"{ccy}_USDT")
            or tickers_map.get(f"{ccy}_USD")
            or tickers_map.get(ccy)
        )
        price = 1.0
        if ticker:
            bid, ask = float(ticker["b"]), float(ticker["k"])
            price = (bid + ask) / 2
        return price

    # derive total notional value
    bal_dfs = list()
    for acct_id, position_balances in acct_position_balances:
        for position_balance in position_balances:
            quantity = float(position_balance["quantity"])
            instrument_name = position_balance["instrument_name"]
            price = get_spot_price(instrument_name)
            position_balance["notional"] = quantity * price
            position_balance["price"] = price
        bal_df = pd.DataFrame(position_balances)
        bal_df = bal_df[bal_df["notional"] > 10]
        bal_df = bal_df.sort_values(by=["notional"], ascending=False)
        bal_df["notional (SGD)"] = bal_df["notional"].map(
            lambda x: f"${x / sgd_usd:,.2f}"
        )
        bal_df["price (SGD)"] = bal_df["price"].map(lambda x: f"${x / sgd_usd:,.2f}")
        bal_df = bal_df[["ccy", "price (SGD)", "notional (SGD)"]]
        bal_dfs.append((acct_id, bal_df))

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    delimiter = "\n\n"
    bal_tables = delimiter.join(
        [f"{acct_id}\n{bal_df.to_string(index=False)}" for acct_id, bal_df in bal_dfs]
    )

    end_time = time.time()
    duration = f"[Finished in {end_time - start_time:,.3f}s]"
    msg = delimiter.join([dt, bal_tables, duration])
    resp = telegram_bot_sendtext("```" + msg + "```")

    return {"statusCode": 200, "body": json.dumps(resp)}


def lambda_handler(event=None, context=None):
    try:
        return main()
    except Exception as err:
        err_msg = f"{err}\n{traceback.format_exc()}"
        telegram_bot_sendtext(err_msg)
    return {"statusCode": 500}


if __name__ == "__main__":
    lambda_handler()
