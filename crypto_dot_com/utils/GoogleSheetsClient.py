import jwt
import json
import requests
from datetime import datetime, timedelta

GET, PUT = "GET", "PUT"
BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
SPREADSHEET_ID_VALUES_RANGE = "/{}/values/{}"


class GoogleSheetsClient:
    """
    Googlesheets Service Account Authenticated Api Client
    """

    def __init__(
        self,
        service_account_json_file: str,
        spreadsheet_id: str = None,
        sheet_id: str = None,
    ):
        self.access_token = self.generate_access_token(service_account_json_file)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id

    @staticmethod
    def generate_access_token(service_account_json_file):
        params = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": GoogleSheetsClient.generate_jwt_token(
                service_account_json_file
            ),
        }
        response = requests.post("https://oauth2.googleapis.com/token", data=params)
        result = response.json()
        if "access_token" not in result:
            print(response, result)
        return result["access_token"]

    @staticmethod
    def generate_jwt_token(service_account_json_file: str):
        with open(service_account_json_file, "r") as file:
            credentials = json.load(file)
        iat = datetime.utcnow()
        exp = iat + timedelta(minutes=60)
        private_key = credentials["private_key"]
        jwt_header = {"alg": "RS256", "typ": "JWT"}
        jwt_payload = {
            "scope": "https://www.googleapis.com/auth/spreadsheets",
            "aud": "https://oauth2.googleapis.com/token",
            "iss": credentials["client_email"],
            "iat": iat,
            "exp": exp,
        }
        jwt_token = jwt.encode(
            jwt_payload, private_key, algorithm="RS256", headers=jwt_header
        )
        return jwt_token

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def request(
        self, method: str, endpoint: str, query_params: dict = None, body: dict = None
    ) -> dict:
        url = BASE_URL + endpoint
        query_params = query_params or {}
        headers = self.get_headers()
        if method == GET:
            resp = requests.get(url, headers=headers, params=query_params)
        elif method == PUT:
            resp = requests.put(url, headers=headers, params=query_params, json=body)
        else:
            raise ValueError(f"Unsupported method={method}")
        return resp.json()

    def parse_spreadsheet_id_and_range(
        self, range: str, spreadsheet_id: str = None, sheet_id: str = None
    ):
        sheet_id = sheet_id or self.sheet_id
        spreadsheet_id = spreadsheet_id or self.spreadsheet_id
        if sheet_id:
            range = f"{self.sheet_id}!{range}"
        return spreadsheet_id, range

    def get_range(
        self, range: str, spreadsheet_id: str = None, sheet_id: str = None
    ) -> list:
        spreadsheet_id, range = self.parse_spreadsheet_id_and_range(
            range, spreadsheet_id, sheet_id
        )
        endpoint = SPREADSHEET_ID_VALUES_RANGE.format(spreadsheet_id, range)
        result = self.request(GET, endpoint)
        return result.get("values", list())

    def get_cell(self, cell: str, spreadsheet_id: str = None, sheet_id: str = None):
        values = self.get_range(
            range=cell, spreadsheet_id=spreadsheet_id, sheet_id=sheet_id
        )
        return values[0][0]

    def update_range(
        self, range: str, values: list, spreadsheet_id: str = None, sheet_id: str = None
    ) -> dict:
        spreadsheet_id, range = self.parse_spreadsheet_id_and_range(
            range, spreadsheet_id, sheet_id
        )
        endpoint = SPREADSHEET_ID_VALUES_RANGE.format(spreadsheet_id, range)
        body = {"values": values}
        query_params = {"valueInputOption": "USER_ENTERED"}
        result = self.request(PUT, endpoint, query_params=query_params, body=body)
        return result

    def update_cell(
        self, range: str, value, spreadsheet_id: str = None, sheet_id: str = None
    ) -> dict:
        return self.update_range(
            range=range,
            values=[[value]],
            spreadsheet_id=spreadsheet_id,
            sheet_id=sheet_id,
        )
