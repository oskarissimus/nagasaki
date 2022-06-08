from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel

from nagasaki.clients.bitclude.dto import AccountInfo, Offer
from nagasaki.clients.deribit_client import AccountSummary
from nagasaki.models.bitclude import OrderbookRest, OrderbookWebsocket


class BitcludeState(BaseModel):
    account_info: Optional[AccountInfo]
    active_offers: Optional[List[Offer]]
    orderbooks: Optional[Dict[str, OrderbookRest]] = defaultdict()
    orderbook_websocket: Optional[OrderbookWebsocket]

    def top_ask(self, asset_symbol):
        return min(self.orderbooks[asset_symbol].asks, key=lambda x: x.price).price

    def top_bid(self, asset_symbol):
        return max(self.orderbooks[asset_symbol].bids, key=lambda x: x.price).price


class DeribitState(BaseModel):
    mark_price: Dict[str, Optional[Decimal]] = defaultdict(None)
    account_summary: Optional[AccountSummary]


class YahooFinanceState(BaseModel):
    usd_pln: Optional[Decimal]


class State(BaseModel):
    yahoo: Optional[YahooFinanceState]
    bitclude: Optional[BitcludeState]
    deribit: Optional[DeribitState]
