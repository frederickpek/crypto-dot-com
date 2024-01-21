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

    def create_order(
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
        """
        Name                Type        Required    Description
        instrument_name     string      Y           e.g. BTCUSD-PERP
        side                string      Y           BUY, SELL
        type                string      Y           LIMIT, MARKET, STOP_LOSS, STOP_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT
        price               string      Y           Price
        quantity            string      Y           Order Quantity
        client_oid          string      N           Client Order ID
        exec_inst           string      N           ["POST_ONLY"]
        time_in_force       string      N           GOOD_TILL_CANCEL, IMMEDIATE_OR_CANCEL, FILL_OR_KILL
        ref_price           string      N*          Trigger price required for STOP_LOSS, STOP_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT order type
        ref_price_type      string      N           which price to use for ref_price: MARK_PRICE (default), INDEX_PRICE, LAST_PRICE
        spot_margin         string      N           SPOT: non-margin order, MARGIN: margin order
        """
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
        response = self.request(method=POST, endpoint=CREATE_ORDER, params=params)
        return response["result"]

    def get_order_detail(self, order_id: str = None, client_oid: str = None) -> dict:
        if not order_id and not client_oid:
            raise ValueError("Either order_id or client_oid must be specified.")
        params = dict()
        if order_id:
            params["order_id"] = order_id
        if client_oid:
            params["client_oid"] = client_oid
        response = self.request(method=POST, endpoint=GET_ORDER_DETAIL, params=params)
        return response.get("result", {})

    def get_instruments(self) -> list[dict]:
        response = self.request(method=GET, endpoint=GET_INSTRUMENTS)
        return response["result"]["data"]
