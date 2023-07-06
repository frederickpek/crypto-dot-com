import json
import aiohttp

from crypto_dot_com.consts import GET, POST, BASE_URL
from crypto_dot_com.utils import get_params_to_str
from crypto_dot_com.sdk.client import CdcClient


class CdcAsyncClient(CdcClient):
    def __init__(self, api_key: str, secret_key: str):
        CdcClient.__init__(self, api_key, secret_key)

    async def request(self, method: str, endpoint: str, params: dict=None) -> dict:
        if method not in (GET, POST):
            raise ValueError('Only GET and POST operations supported.')
        try:
            params = params or {}
            async with aiohttp.ClientSession() as session:
                if method == GET:
                    query_params = get_params_to_str(params)
                    url = BASE_URL + endpoint + '?' + query_params
                    async with session.get(url) as resp:
                        resp = await resp.json()
                        return resp
                elif method == POST:
                    body = self.get_post_payload_body(endpoint, params)
                    url = BASE_URL + endpoint
                    async with session.post(url, json=body) as resp:
                        resp = await resp.json()
                        return resp
        except Exception:
            pass
        return dict()

