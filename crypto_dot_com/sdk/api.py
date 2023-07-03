from crypto_dot_com.consts import POST, USER_BALANCE, USER_BALANCE_HISTORY, POSITIONS
from crypto_dot_com.sdk.client import CdcClient


class CdcApi(CdcClient):
    def __init__(self, api_key: str, secret_key: str):
        CdcClient.__init__(self, api_key, secret_key)
    
    def get_user_balance(self) -> dict:
        response = self.request(method=POST, endpoint=USER_BALANCE)
        return response['result']['data'][0]

    def get_user_balance_history(self, timeframe: str=None, end_time: int=None, limit: int=None) -> list[dict]:
        """
            timeframe	string	Optional	'H1' means every hour, 'D1' means every day. Omit for 'D1'
            end_time	number	Optional	Can be millisecond or nanosecond. Exclusive. If not provided, will be current time.
            limit	    int	    Optional	If timeframe is D1, max limit will be 30 (days). If timeframe is H1, max limit will be 120 (hours).
        """
        params = dict()
        if timeframe:
            params['timeframe'] = timeframe
        if end_time:
            params['end_time'] = end_time
        if limit:
            params['limit'] = limit
        response = self.request(method=POST, endpoint=USER_BALANCE_HISTORY, params=params)
        return response['result']['data']

    def get_positions(self, instrument_name: str=None) -> list[dict]:
        params = dict()
        if instrument_name:
            params['instrument_name'] = instrument_name
        response = self.request(method=POST, endpoint=POSITIONS, params=params)
        return response['result']['data']

