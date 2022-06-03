from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from nagasaki.clients.bitclude.dto import (
    AccountInfo,
    Offer,
)
from nagasaki.clients.deribit_client import AccountSummary
from nagasaki.models.bitclude import (
    OrderbookRest,
    OrderbookWebsocket,
)


class BitcludeState(BaseModel):
    account_info: Optional[AccountInfo]
    active_offers: Optional[List[Offer]]
    orderbook_rest: Optional[OrderbookRest]
    orderbook_websocket: Optional[OrderbookWebsocket]

    def top_ask(self):
        return min(self.orderbook_rest.asks, key=lambda x: x.price).price

    def top_bid(self):
        return max(self.orderbook_rest.bids, key=lambda x: x.price).price


class DeribitState(BaseModel):
    btc_mark_usd: Optional[Decimal]
    account_summary: Optional[AccountSummary]


class State(BaseModel):
    usd_pln: Optional[Decimal]
    bitclude: Optional[BitcludeState]
    deribit: Optional[DeribitState]

    def get_top_ask(self) -> Decimal:
        return min(self.bitclude.orderbook_rest.asks, key=lambda x: x.price).price

    def get_top_bid(self) -> Decimal:
        return max(self.bitclude.orderbook_rest.bids, key=lambda x: x.price).price

    @property
    def grand_total_delta(self) -> Decimal:
        bitclude_btcs = self.bitclude.account_info.btcs
        deribit_total_delta = (
            self.deribit.account_summary.margin_balance
            + self.deribit.account_summary.delta_total
        )
        return bitclude_btcs + deribit_total_delta
