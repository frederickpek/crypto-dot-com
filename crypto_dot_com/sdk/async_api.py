from crypto_dot_com.consts import (
    GET,
    POST,
    USER_BALANCE,
    USER_BALANCE_HISTORY,
    POSITIONS,
    GET_TICKERS,
    GET_CANDLESTICK,
)
from crypto_dot_com.sdk.async_client import CdcAsyncClient


class CdcAsyncApi(CdcAsyncClient):
    def __init__(self, api_key: str, secret_key: str):
        CdcAsyncClient.__init__(self, api_key, secret_key)

    async def get_user_balance(self) -> dict:
        response = await self.request(method=POST, endpoint=USER_BALANCE)
        data = response["result"]["data"][0]
        for d in data["position_balances"]:
            d["ccy"] = d["instrument_name"]
        return data

    async def get_user_balance_history(
        self, timeframe: str = None, end_time: int = None, limit: int = None
    ) -> list[dict]:
        """
        timeframe   string  Optional    'H1' means every hour, 'D1' means every day. Omit for 'D1'
        end_time    number  Optional    Can be millisecond or nanosecond. Exclusive. If not provided, will be current time.
        limit       int     Optional    If timeframe is D1, max limit will be 30 (days). If timeframe is H1, max limit will be 120 (hours).
        """
        params = dict()
        if timeframe:
            params["timeframe"] = timeframe
        if end_time:
            params["end_time"] = end_time
        if limit:
            params["limit"] = limit
        response = await self.request(
            method=POST, endpoint=USER_BALANCE_HISTORY, params=params
        )
        return response["result"]["data"]

    async def get_positions(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = await self.request(method=POST, endpoint=POSITIONS, params=params)
        return response["result"]["data"]

    async def get_tickers(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = await self.request(method=GET, endpoint=GET_TICKERS, params=params)
        return response["result"]["data"]

    async def get_candlestick(
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
        response = await self.request(
            method=GET, endpoint=GET_CANDLESTICK, params=params
        )
        return response["result"]["data"]
