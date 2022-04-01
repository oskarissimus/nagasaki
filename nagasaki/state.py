from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from nagasaki.clients.bitclude.dto import (
    AccountInfo,
    Offer,
)
from nagasaki.models.bitclude import (
    OrderbookRest,
    OrderbookWebsocket,
)


class BitcludeState(BaseModel):
    account_info: Optional[AccountInfo]
    active_offers: Optional[List[Offer]]
    orderbook_rest: Optional[OrderbookRest]
    orderbook_websocket: Optional[OrderbookWebsocket]


class DeribitState(BaseModel):
    btc_mark_usd: Optional[Decimal]


class State(BaseModel):
    usd_pln: Optional[Decimal]
    bitclude: Optional[BitcludeState]
    deribit: Optional[DeribitState]

    def get_top_ask(self) -> Decimal:
        return min(self.bitclude.orderbook_rest.asks, key=lambda x: x.price).price
