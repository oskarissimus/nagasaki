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

    class Config:
        fields = {
            "exchange_balance": {"include": True},
            "mark_price": {"include": True},
        }


class State(BaseModel):
    exchange_states: Dict[str, ExchangeState] = defaultdict(lambda: None)


class BitcludeState(ExchangeState):
    account_info: Optional[AccountInfo]
    active_offers: Optional[List[Offer]]
    orderbooks: Optional[Dict[str, OrderbookRest]] = defaultdict(lambda: None)

    def top_ask(self, asset_symbol):
        return min(self.orderbooks[asset_symbol].asks, key=lambda x: x.price).price

    def top_bid(self, asset_symbol):
        return max(self.orderbooks[asset_symbol].bids, key=lambda x: x.price).price

    def mid_price(self, asset_symbol):
        return (self.top_ask(asset_symbol) + self.top_bid(asset_symbol)) / 2

    class Config:
        fields = {
            "orderbooks": {"include": True},
        }


class DeribitState(ExchangeState):
    account_summary: Optional[AccountSummary]

    class Config:
        fields = {
            "account_summary": {"include": True},
        }


class YahooFinanceState(ExchangeState):
    pass
