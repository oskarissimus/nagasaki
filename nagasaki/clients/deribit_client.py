from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel
import requests

from nagasaki.clients.base_client import BaseClient, OrderTaker
from nagasaki.enums.common import SideTypeEnum
from nagasaki.logger import logger


class DeribitClientException(Exception):
    pass


class AccountSummary(BaseModel):
    equity: Decimal
    delta_total: Decimal
    margin_balance: Decimal


class DeribitClient(BaseClient):
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
        https://www.deribit.com/api/v2
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

    @property
    def headers_with_token(self):
        if self.token is None:
            self.get_token()
        if self.token_expiration_seconds_left() < 60:
            self.get_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def fetch_account_summary(self) -> AccountSummary:

        params = (
            ("currency", "BTC"),
            ("extended", "true"),
        )

        response = requests.get(
            f"{self.deribit_url_base}/private/get_account_summary",
            headers=self.headers_with_token,
            params=params,
        )
        response_json = response.json()
        if "error" in response_json:
            raise DeribitClientException(response_json["error"])
        return AccountSummary(**response_json["result"])

    def create_order(self, order: OrderTaker):
        order_type = "buy" if order.side == SideTypeEnum.BID else "sell"
        self.create_order_perpetual(order.amount, order_type)

    def create_order_perpetual(self, amount_in_usd, order_type, dry_run=False):
        if order_type in ("buy", "sell"):
            rounded_amount_in_usd = round(amount_in_usd, -1)
            if dry_run:
                logger.info("DRY RUN: ")
            logger.info(
                f"{order_type} at market BTC-PERPETUAL {rounded_amount_in_usd:.2f} USD"
            )
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
            headers=self.headers_with_token,
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

    def fetch_index_price_eth_usd(self) -> Decimal:
        response = requests.get(
            f"{self.deribit_url_base}/public/get_index_price?index_name=eth_usd"
        )
        return Decimal(response.json()["result"]["index_price"])

    def cancel_order(self, order: OrderTaker):
        pass

    def cancel_and_wait(self, order: OrderTaker):
        pass
