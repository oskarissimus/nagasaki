from datetime import datetime, timedelta
from decimal import Decimal

import ccxt
import requests
from pydantic import BaseModel

from nagasaki.clients.base_client import BaseClient, OrderTaker
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.logger import logger


class DeribitClientException(Exception):
    pass


class AccountSummary(BaseModel):
    equity: Decimal
    delta_total: Decimal
    margin_balance: Decimal


class DeribitClient(BaseClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        url_base: str = "https://www.deribit.com/api/v2",
    ):
        self.url_base = url_base
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiration = None
        self.ccxt_connector = ccxt.deribit(
            {"apiKey": self.client_id, "secret": self.client_secret}
        )

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
            ("client_id", self.client_id),
            ("client_secret", self.client_secret),
            ("grant_type", "client_credentials"),
        )

        response = requests.get(
            f"{self.url_base}/public/auth", headers=headers, params=params
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

    def fetch_account_summary(self, currency: str) -> AccountSummary:
        response = self.ccxt_connector.fetch_balance({"currency": currency})
        return AccountSummary(**response["info"]["result"])

    def create_order(self, order: OrderTaker):
        order_type = "buy" if order.side == SideTypeEnum.BID else "sell"
        self.create_order_perpetual(order.amount, order_type, order.instrument)

    def create_order_perpetual(self, amount_in_usd, order_type, instrument):
        rounded_amount_in_usd = round(amount_in_usd, -1)

        logger.info(
            f"{order_type} at market {instrument.name}: {rounded_amount_in_usd:.2f} USD"
        )

        params = self.create_order_request_params(rounded_amount_in_usd, instrument)
        response = requests.get(
            f"{self.url_base}/private/{order_type}",
            headers=self.headers_with_token,
            params=params,
        )

        data = response.json()

        return data

    def fetch_index_price_in_usd(self, instrument: InstrumentTypeEnum) -> Decimal:
        symbol = f"{instrument.market_1}/USD:{instrument.market_1}"
        response = self.ccxt_connector.fetch_ticker(symbol)
        return Decimal(response["info"]["index_price"])

    def cancel_order(self, order: OrderTaker):
        pass

    def cancel_and_wait(self, order: OrderTaker):
        pass

    @staticmethod
    def create_order_request_params(
        amount_in_usd: Decimal, instrument: InstrumentTypeEnum
    ):
        instrument_name = "-".join(instrument.value)

        return (
            ("amount", float(amount_in_usd)),
            ("instrument_name", instrument_name),
            ("time_in_force", "good_til_cancelled"),
            ("type", "market"),
        )
