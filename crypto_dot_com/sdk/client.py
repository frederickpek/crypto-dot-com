import hmac
import hashlib
import requests

from crypto_dot_com.consts import GET, POST, BASE_URL
from crypto_dot_com.utils import (
    get_params_to_str,
    post_params_to_str,
    get_nonce,
    get_id,
)


class CdcClient:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    def get_signature(self, payload_str: str) -> str:
        return hmac.new(
            bytes(str(self.secret_key), "utf-8"),
            msg=bytes(payload_str, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def get_post_payload_body(self, endpoint: str, params: dict) -> dict:
        identifier = get_id()
        api_key = self.api_key
        nonce = get_nonce()
        param_str = post_params_to_str(params)
        payload_str = endpoint + str(identifier) + api_key + param_str + str(nonce)
        signature = self.get_signature(payload_str)
        return {
            "id": identifier,
            "params": params,
            "method": endpoint,
            "api_key": self.api_key,
            "nonce": nonce,
            "sig": signature,
        }

    def request(self, method: str, endpoint: str, params: dict = None) -> dict:
        if method not in (GET, POST):
            raise ValueError("Only GET and POST operations supported.")
        try:
            params = params or {}
            if method == GET:
                query_params = get_params_to_str(params)
                resp = requests.get(BASE_URL + endpoint + "?" + query_params)
            elif method == POST:
                body = self.get_post_payload_body(endpoint, params)
                resp = requests.post(BASE_URL + endpoint, json=body)
        except Exception:
            return dict()
        return resp.json()
