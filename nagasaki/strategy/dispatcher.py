from decimal import Decimal
from typing import List

from pydantic import BaseModel

from nagasaki.clients import BaseClient
from nagasaki.clients.bitclude.dto import Offer
from nagasaki.enums.common import SideTypeEnum
from nagasaki.logger import logger
from nagasaki.models.bitclude import Order
from nagasaki.state import BitcludeState


class Tolerance(BaseModel):
    price: Decimal
    amount: Decimal


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
        client: BaseClient,
        bitclude_state: BitcludeState,
        tolerance: Tolerance = None,
    ):
        self.client = client
        self.tolerance = tolerance or Tolerance(
            price=Decimal("100"), amount=Decimal("0.000_3")
        )
        self.bitclude_state = bitclude_state

    def dispatch(self, desirable_order: Order):
        if self.has_exactly_one_own_offer(desirable_order.side):
            logger.info("Has exactly one own offer")
            if offer_is_within_tolerance(
                self.active_offers[0], desirable_order, self.tolerance
            ):
                logger.info("Offer is within tolerance")
                return

        logger.debug(self.active_offers)
        for offer in self.active_offers:
            if offer.offertype == desirable_order.side:
                self.client.cancel_order(offer.to_order_maker())

        self.client.create_order(desirable_order)

    @property
    def active_offers(self) -> List[Offer]:
        return self.bitclude_state.active_offers or []

    def has_exactly_one_own_offer(self, side: SideTypeEnum) -> bool:
        offers = [offer for offer in self.active_offers if offer.offertype == side]
        return len(offers) == 1
