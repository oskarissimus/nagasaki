from decimal import Decimal
from typing import List

from pydantic import BaseModel

from nagasaki.clients import ExchangeClient
from nagasaki.clients.bitclude.dto import Offer
from nagasaki.enums.common import SideTypeEnum
from nagasaki.logger import logger
from nagasaki.models.bitclude import Order
from nagasaki.state import BitcludeState


class Tolerance(BaseModel):
    price: Decimal
    amount: Decimal

    def __str__(self):
        return f"price_tolerance = +/-{self.price:.4f}; amount_tolerance = +/-{self.amount:.4f}"


def offer_is_within_tolerance(
    offer: Offer,
    desirable_order: Order,
    tolerance: Tolerance,
):
    return (
        abs(offer.price - desirable_order.price) < tolerance.price
        and abs(offer.amount - desirable_order.amount) < tolerance.amount
    )


class StrategyOrderDispatcher:
    def __init__(
        self,
        client: ExchangeClient,
        bitclude_state: BitcludeState,
        tolerance: Tolerance = None,
    ):
        self.client = client
        self.tolerance = tolerance or Tolerance(price=Decimal("0"), amount=Decimal("0"))
        self.bitclude_state = bitclude_state

    def dispatch(self, desirable_order: Order):
        if self.has_exactly_one_own_offer(desirable_order.side):
            own_offer = self.get_list_of_active_offers_for_side(desirable_order.side)[0]
            logger.info(f"Has exactly one own offer: {own_offer}")
            if offer_is_within_tolerance(
                self.active_offers[0], desirable_order, self.tolerance
            ):
                logger.info(f"Offer is within tolerance: {self.tolerance}")
                return

        logger.info(f"all active offers: {self.active_offers}")
        for offer in self.active_offers:
            if offer.offertype == desirable_order.side:
                self.client.cancel_order(offer.to_order_maker())

        self.client.create_order(desirable_order)

    @property
    def active_offers(self) -> List[Offer]:
        return self.bitclude_state.active_offers or []

    def get_list_of_active_offers_for_side(self, side: SideTypeEnum) -> List[Offer]:
        return [offer for offer in self.active_offers if offer.offertype == side]

    def has_exactly_one_own_offer(self, side: SideTypeEnum) -> bool:
        offers = self.get_list_of_active_offers_for_side(side)
        return len(offers) == 1
