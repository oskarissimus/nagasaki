from collections import defaultdict
from decimal import Decimal
from typing import List, Optional, Dict

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
    orderbooks: Optional[Dict[str, OrderbookRest]] = defaultdict()
    orderbook_rest: Optional[OrderbookRest]
    orderbook_websocket: Optional[OrderbookWebsocket]

    def top_ask(self, asset_symbol):
        return min(self.orderbooks[asset_symbol].asks, key=lambda x: x.price).price

    def top_bid(self, asset_symbol):
        return max(self.orderbooks[asset_symbol].bids, key=lambda x: x.price).price


class DeribitState(BaseModel):
    mark_price: Dict[str, Optional[Decimal]] = defaultdict(None)
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
