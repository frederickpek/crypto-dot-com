from crypto_dot_com.consts import (
    GET,
    POST,
    USER_BALANCE,
    USER_BALANCE_HISTORY,
    POSITIONS,
    GET_TICKERS,
    GET_CANDLESTICK,
    OPEN_ORDERS,
)
from crypto_dot_com.sdk.client import CdcClient


class CdcApi(CdcClient):
    def __init__(self, api_key: str, secret_key: str):
        CdcClient.__init__(self, api_key, secret_key)

    def get_user_balance(self) -> dict:
        response = self.request(method=POST, endpoint=USER_BALANCE)
        data = response["result"]["data"][0]
        for d in data["position_balances"]:
            d["ccy"] = d["instrument_name"]
        return data

    def get_user_balance_history(
        self, timeframe: str = None, end_time: int = None, limit: int = None
    ) -> list[dict]:
        params = dict()
        if timeframe:
            params["timeframe"] = timeframe
        if end_time:
            params["end_time"] = end_time
        if limit:
            params["limit"] = limit
        response = self.request(
            method=POST, endpoint=USER_BALANCE_HISTORY, params=params
        )
        return response["result"]["data"]

    def get_positions(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = self.request(method=POST, endpoint=POSITIONS, params=params)
        return response["result"]["data"]

    def get_tickers(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = self.request(method=GET, endpoint=GET_TICKERS, params=params)
        return response["result"]["data"]

    def get_candlestick(
        self,
        instrument_name: str,
        timeframe: str = None,
        count: int = None,
        start_ts: int = None,
        end_ts: int = None,
    ) -> list[dict]:
        params = dict()
        params["instrument_name"] = instrument_name
        if timeframe:
            params["timeframe"] = timeframe
        if count:
            params["count"] = count
        if start_ts:
            params["start_ts"] = start_ts
        if end_ts:
            params["end_ts"] = end_ts
        response = self.request(method=GET, endpoint=GET_CANDLESTICK, params=params)
        return response["result"]["data"]

    def get_open_orders(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = self.request(method=POST, endpoint=OPEN_ORDERS, params=params)
        return response["result"]["data"]
