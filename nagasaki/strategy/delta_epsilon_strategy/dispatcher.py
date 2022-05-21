from decimal import Decimal
from typing import List

from pydantic import BaseModel

from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderMaker
from nagasaki.clients.bitclude.dto import Offer
from nagasaki.state import State


class Tolerance(BaseModel):
    price: Decimal
    amount: Decimal


def offer_is_within_tolerance(
    offer: Offer,
    desirable_order: OrderMaker,
    tolerance: Tolerance,
):
    return (
        abs(offer.price - desirable_order.price) < tolerance.price
        and abs(offer.amount - desirable_order.amount) < tolerance.amount
    )


class StrategyOrderDispatcher:
    def __init__(self, client: BaseClient, tolerance: Tolerance, state: State):
        self.client = client
        self.tolerance = tolerance or Tolerance(
            price=Decimal("100"), amount=Decimal("0.000_3")
        )
        self.state = state

    def dispatch(self, desirable_order):
        if self.has_exactly_one_own_offer:
            if offer_is_within_tolerance(
                self.active_offers[0], desirable_order, self.tolerance
            ):
                return

        for offer in self.active_offers:
            self.client.cancel_and_wait(offer.to_order_maker())

        self.client.create_order(desirable_order)

    @property
    def active_offers(self) -> List[Offer]:
        return self.state.bitclude.active_offers or []

    @property
    def has_exactly_one_own_offer(self):
        return len(self.active_offers) == 1
