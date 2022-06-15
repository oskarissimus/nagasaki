from decimal import Decimal

import ccxt
from pydantic import BaseModel

from nagasaki.clients.base_client import BaseClient, OrderTaker
from nagasaki.clients.bitclude.dto import CreateRequestDTO
from nagasaki.enums.common import InstrumentTypeEnum


class AccountSummary(BaseModel):
    equity: Decimal
    delta_total: Decimal
    margin_balance: Decimal


class DeribitClient(BaseClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.ccxt_connector = ccxt.deribit(
            {"apiKey": self.client_id, "secret": self.client_secret}
        )

    def fetch_account_summary(self, currency: str) -> AccountSummary:
        response = self.ccxt_connector.fetch_balance({"currency": currency})
        return AccountSummary(**response["info"]["result"])

    def create_order(self, order: OrderTaker) -> None:
        self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order_taker(order).to_method_params()
        )

    def fetch_index_price_in_usd(self, instrument: InstrumentTypeEnum) -> Decimal:
        symbol = f"{instrument.market_1}/USD:{instrument.market_1}"
        response = self.ccxt_connector.fetch_ticker(symbol)
        return Decimal(response["info"]["index_price"])

    def cancel_order(self, order: OrderTaker):
        pass
