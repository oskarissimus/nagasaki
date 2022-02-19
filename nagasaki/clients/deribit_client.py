import requests
from pydantic import BaseModel
from datetime import datetime, timedelta
from decimal import *

getcontext().prec = 10


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

    def get_total_delta(self) -> float:
        """
        D = get delta position from api delta_total
        MB = get margin balance from api margin_balance
        MB - sald BTC na deribicie
        grand_total_delta = MB + D
        """
        if self.account_summary is None:
            raise DeribitClientException(
                "account_summary attribute of this object is None, please run fetch_account_summary() method to initialize it!"
            )
        return self.account_summary.margin_balance + self.account_summary.delta_total

    def get_equity_usd(self):
        """
        get private-get_account_summary   ›  equity 	number 	The account's current equity
        """
        if self.account_summary is None:
            raise DeribitClientException(
                "account_summary attribute of this object is None, please run fetch_account_summary() method to initialize it!"
            )
        if self.index_price_btc_usd is None:
            raise DeribitClientException(
                "index_price_btc_usd attribute of this object is None, please run fetch_index_price_btc_usd() method to initialize it!"
            )
        equity_btc = self.account_summary.equity
        equity_usd = equity_btc * self.index_price_btc_usd
        return equity_usd

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

    def fetch_get_funding_rate_history(
        self,
        start_timestamp_microseconds,
        end_timestamp_microseconds,
        instrument="BTC-PERPETUAL",
    ):
        response = requests.get(
            f"{self.deribit_url_base}/public/get_funding_rate_history?&start_timestamp={start_timestamp_microseconds}&end_timestamp={end_timestamp_microseconds}&instrument_name={instrument}"
        )
        response_json = response.json()
        current = 1
        total_interest = 0
        for d in response_json["result"]:
            total_interest = total_interest + d["interest_1h"]
            current = current * (1 + d["interest_1h"])
        self.perp_yield = round(((current ** 12) - 1) * 100, 4)
