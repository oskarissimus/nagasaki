from decimal import Decimal
from typing import List

from pydantic import BaseModel

from nagasaki.enums.common import SideTypeEnum
from nagasaki.models.bitclude import BitcludeOrder
from nagasaki.clients.bitclude.models import AccountInfo, AccountHistory, Offer


class State:

    ask_orderbook = []
    bid_orderbook = []

    # TODO: Seed state with current ticker.

    bitclude_account_info: AccountInfo = None
    btc_mark_usd: Decimal = None
    usd_pln: Decimal = None
    bitclude_active_offers: List[Offer] = None

    def get_own_bid_max(self) -> BitcludeOrder:
        if len(self.bitclude_active_offers) >= 1:
            own_bid_offers = [
                offer
                for offer in self.bitclude_active_offers
                if offer.offertype == SideTypeEnum.BID
            ]
            if len(own_bid_offers) >= 1:
                own_bid_max_offer = max(own_bid_offers, key=lambda offer: offer.price)
                return BitcludeOrder(
                    side=own_bid_max_offer.offertype,
                    price=own_bid_max_offer.price,
                    order_id=own_bid_max_offer.nr,
                    amount=own_bid_max_offer.amount,
                )

    def get_own_ask_min(self) -> BitcludeOrder:
        if len(self.bitclude_active_offers) >= 1:
            own_ask_offers = [
                offer
                for offer in self.bitclude_active_offers
                if offer.offertype == SideTypeEnum.ASK
            ]
            if len(own_ask_offers) >= 1:
                own_ask_min_offer = min(own_ask_offers, key=lambda offer: offer.price)
                print(f"HEHEHE {own_ask_min_offer.nr}")
                return BitcludeOrder(
                    side=own_ask_min_offer.offertype,
                    price=own_ask_min_offer.price,
                    order_id=own_ask_min_offer.nr,
                    amount=own_ask_min_offer.amount,
                )

    def get_top_bid(self) -> Decimal:
        return max(self.bid_orderbook)

    def get_top_ask(self) -> Decimal:
        return min(self.ask_orderbook)

    def clear(self):
        self.ask_orderbook = []
        self.bid_orderbook = []
        self.own_ask = None
        self.own_bid = None
        self.bitclude_account_info = None


class BitcludeState(BaseModel):
    account_info: AccountInfo
    account_history: AccountHistory
