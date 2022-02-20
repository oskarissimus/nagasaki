from datetime import datetime, timedelta
from decimal import Decimal

import requests
from pydantic import BaseModel


class DeribitClientException(Exception):
    pass


class AccountSummary(BaseModel):
    equity: float
    delta_total: float
    margin_balance: float


class DeribitClient:
    def __init__(
        self, deribit_url_base: str, deribit_client_id: str, deribit_client_secret: str
    ):
        self.deribit_url_base = deribit_url_base
        self.deribit_client_id = deribit_client_id
        self.deribit_client_secret = deribit_client_secret
        self.token = None
        self.token_expiration = None

    def get_token(self) -> True:
        """
        method gets deribit access token using
        - `self.deribit_url_base`
        - `self.deribit_client_id`
        - `self.deribit_client_secret`

        and writes it into `self.token` for further use in client requests
        """
        headers = {
            "Content-Type": "application/json",
        }

        params = (
            ("client_id", self.deribit_client_id),
            ("client_secret", self.deribit_client_secret),
            ("grant_type", "client_credentials"),
        )

        response = requests.get(
            f"{self.deribit_url_base}/public/auth", headers=headers, params=params
        )
        data = response.json()
        if "result" in data:
            self.token = data["result"]["access_token"]
            self.token_expiration = datetime.now() + timedelta(
                seconds=data["result"]["expires_in"]
            )
            return True
        else:
            raise DeribitClientException(data["error"])

    def token_expiration_seconds_left(self):

        if self.token_expiration is None:
            raise DeribitClientException(
                "token_expiration attribute of this object is None, please run get_token() method to initialize it!"
            )
        return (self.token_expiration - datetime.now()).total_seconds()

    def get_headers_with_token(self):
        if self.token is None:
            raise DeribitClientException(
                "token attribute of this object is None, please run get_token() method to initialize it!"
            )
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def fetch_account_summary(self) -> dict:

        params = (
            ("currency", "BTC"),
            ("extended", "true"),
        )

        response = requests.get(
            f"{self.deribit_url_base}/private/get_account_summary",
            headers=self.get_headers_with_token(),
            params=params,
        )
        response_json = response.json()
        if "error" in response_json:
            raise DeribitClientException(response_json["error"])
        return AccountSummary(**response_json["result"])

    def create_order_perpetual(self, amount_in_usd, order_type, dry_run=False):
        if order_type in ("buy", "sell"):
            rounded_amount_in_usd = round(amount_in_usd, -1)
            if dry_run:
                print("DRY RUN: ", end="")
            print(f"{order_type} at market BTC-PERPETUAL {rounded_amount_in_usd} USD")
            if dry_run:
                return True

        params = (
            ("amount", rounded_amount_in_usd),
            ("instrument_name", "BTC-PERPETUAL"),
            ("time_in_force", "good_til_cancelled"),
            ("type", "market"),
        )

        response = requests.get(
            f"{self.deribit_url_base}/private/{order_type}",
            headers=self.get_headers_with_token(),
            params=params,
        )

        data = response.json()

        return data

    def sell_perpetual(self, amount_in_usd, dry_run=False):
        return self.create_order_perpetual(amount_in_usd, "sell", dry_run=dry_run)

    def buy_perpetual(self, amount_in_usd, dry_run=False):
        return self.create_order_perpetual(amount_in_usd, "buy", dry_run=dry_run)

    def fetch_index_price_btc_usd(self) -> Decimal:
        response = requests.get(
            f"{self.deribit_url_base}/public/get_index_price?index_name=btc_usd"
        )
        return Decimal(response.json()["result"]["index_price"])
