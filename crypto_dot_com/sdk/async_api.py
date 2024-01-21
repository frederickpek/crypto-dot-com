from crypto_dot_com.consts import (
    GET,
    POST,
    USER_BALANCE,
    USER_BALANCE_HISTORY,
    POSITIONS,
    GET_TICKERS,
    GET_CANDLESTICK,
    OPEN_ORDERS,
    CREATE_ORDER,
    GET_ORDER_DETAIL,
    GET_INSTRUMENTS,
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
        return response.get("result", {}).get("data", [])

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

    async def get_open_orders(self, instrument_name: str = None) -> list[dict]:
        params = dict()
        if instrument_name:
            params["instrument_name"] = instrument_name
        response = await self.request(method=POST, endpoint=OPEN_ORDERS, params=params)
        return response["result"]["data"]

    async def create_order(
        self,
        instrument_name: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str = None,
        client_oid: str = None,
        exec_inst: list[str] = None,
        time_in_force: str = None,
        ref_price: str = None,
        ref_price_type: str = None,
        spot_margin: str = None,
    ) -> dict:
        params = dict()
        params["instrument_name"] = instrument_name
        params["side"] = side
        params["type"] = order_type
        params["quantity"] = quantity
        if price:
            params["price"] = price
        if client_oid:
            params["client_oid"] = client_oid
        if exec_inst:
            params["exec_inst"] = exec_inst
        if time_in_force:
            params["time_in_force"] = time_in_force
        if ref_price:
            params["ref_price"] = ref_price
        if ref_price_type:
            params["ref_price_type"] = ref_price_type
        if spot_margin:
            params["spot_margin"] = spot_margin
        response = await self.request(method=POST, endpoint=CREATE_ORDER, params=params)
        return response["result"]

    async def get_order_detail(
        self, order_id: str = None, client_oid: str = None
    ) -> dict:
        if not order_id and not client_oid:
            raise ValueError("Either order_id or client_oid must be specified.")
        params = dict()
        if order_id:
            params["order_id"] = order_id
        if client_oid:
            params["client_oid"] = client_oid
        response = await self.request(
            method=POST, endpoint=GET_ORDER_DETAIL, params=params
        )
        return response.get("result", {})

    async def get_instruments(self) -> list[dict]:
        response = await self.request(method=GET, endpoint=GET_INSTRUMENTS)
        return response["result"]["data"]
