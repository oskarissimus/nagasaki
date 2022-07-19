from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel

from nagasaki.clients.bitclude.dto import AccountInfo, Offer
from nagasaki.clients.dto import ExchangeBalance
from nagasaki.models.bitclude import AccountSummary, OrderbookRest


class ExchangeState(BaseModel):
    exchange_balance: Optional[ExchangeBalance]
    mark_price: Dict[str, Optional[Decimal]] = defaultdict(lambda: None)


class BitcludeState(ExchangeState):
    account_info: Optional[AccountInfo]
    active_offers: Optional[List[Offer]]
    orderbooks: Optional[Dict[str, OrderbookRest]] = defaultdict(lambda: None)

    def top_ask(self, asset_symbol):
        return min(self.orderbooks[asset_symbol].asks, key=lambda x: x.price).price

    def top_bid(self, asset_symbol):
        return max(self.orderbooks[asset_symbol].bids, key=lambda x: x.price).price


class DeribitState(ExchangeState):
    account_summary: Optional[AccountSummary]


class YahooFinanceState(ExchangeState):
    pass
