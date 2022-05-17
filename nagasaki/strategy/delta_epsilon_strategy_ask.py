from decimal import Decimal
from typing import List

from pydantic import BaseModel
from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderMaker
from nagasaki.clients.bitclude.dto import Offer
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum, InstrumentTypeEnum
from nagasaki.models.bitclude import Action, BitcludeOrder
from nagasaki.strategy.abstract_strategy import AbstractStrategy, StrategyException
from nagasaki.state import State


def calculate_btc_value_in_pln(btc: Decimal, price: Decimal) -> Decimal:
    return btc * price


def calculate_inventory_parameter(
    total_pln: Decimal, total_btc_value_in_pln: Decimal
) -> Decimal:
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1


def calculate_delta_adjusted_for_inventory(inventory_parameter):
    A = Decimal("-0.0035")
    B = Decimal("0.0055")
    res = A * inventory_parameter + B
    if res <= 0:
        raise StrategyException(f"Delta is too small for inventory parameter: {res}")
    return res


def calculate_delta_price(deribit_mark_price: Decimal, delta: Decimal) -> Decimal:
    """
    delta price is distanced from deribit mark price depending on inventory parameter
    """
    return deribit_mark_price * (1 + delta)


def calculate_epsilon_price(top_ask: Decimal, epsilon: Decimal) -> Decimal:
    """
    epsilon price is distanced from bitclude top ask by epsilon in PLN
    """
    return top_ask - epsilon


class Tolerance(BaseModel):
    price: Decimal
    amount: Decimal


def offer_is_within_tolerance(
    offer: BitcludeOrder,
    desirable_order: BitcludeOrder,
    tolerance: Tolerance,
):
    return (
        abs(offer.price - desirable_order.price) < tolerance.price
        and abs(offer.amount - desirable_order.amount) < tolerance.amount
    )


def actions_for_0_own_offers(desirable_action: Action):
    return [desirable_action]


def actions_for_1_own_offer(
    desirable_action: Action, own_offer: Offer, tolerance: Tolerance
):
    if offer_is_within_tolerance(own_offer, desirable_action.order, tolerance):
        return []
    return [cancel_action(own_offer), desirable_action]


def actions_for_more_than_1_own_offer(
    desirable_action: Action,
    own_offers: List[Offer],
):
    """
    if there are more than 1 own offers, cancel all and create desirable action
    """
    return cancel_all_asks(own_offers) + [desirable_action]


def cancel_all_asks(active_offers: List[Offer]):
    actions = []
    asks = [offer for offer in active_offers if offer.offertype == SideTypeEnum.ASK]
    for offer in asks:
        actions.append(cancel_action(offer))
    return actions


def ask_action(price: Decimal, amount: Decimal):
    return Action(
        action_type=ActionTypeEnum.CREATE,
        order=BitcludeOrder(
            side=SideTypeEnum.ASK,
            price=price,
            amount=amount,
        ),
    )


def ask_order(price: Decimal, amount: Decimal) -> OrderMaker:
    return OrderMaker(
        side=SideTypeEnum.ASK,
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


def cancel_action(offer: Offer):
    Action(
        action_type=ActionTypeEnum.CANCEL_AND_WAIT,
        order=offer.to_bitclude_order(),
    )


class DeltaEpsilonStrategyAsk(AbstractStrategy):
    def __init__(self, state: State, client: BaseClient):
        self.state = state
        self.client = client
        self.epsilon = Decimal("0.01")
        self.price_tolerance = Decimal("100")
        self.amount_tolerance = Decimal("0.000_3")
        self.tolerance = Tolerance(
            price=self.price_tolerance, amount=self.amount_tolerance
        )

    def get_actions(self) -> List[Action]:
        delta_price = calculate_delta_price(self.ref, self.delta_adjusted_for_inventory)
        epsilon_price = calculate_epsilon_price(self.top_ask, self.epsilon)

        desirable_price = max(delta_price, epsilon_price)
        desirable_amount = self.total_btc
        desirable_action = ask_action(desirable_price, desirable_amount)
        desirable_order = ask_order(desirable_price, desirable_amount)

        own_offers = self.state.bitclude.active_offers

        if len(own_offers) == 0:
            self.client.create_order(desirable_order)

        if len(own_offers) == 1:
            return actions_for_1_own_offer(
                desirable_action, own_offers[0], self.tolerance
            )

        return actions_for_more_than_1_own_offer(desirable_action, own_offers)

    @property
    def top_ask(self):
        return min(self.state.bitclude.orderbook_rest.asks, key=lambda x: x.price).price

    @property
    def total_btc(self):
        return (
            self.state.bitclude.account_info.balances["BTC"].active
            + self.state.bitclude.account_info.balances["BTC"].inactive
        )

    @property
    def ref(self):
        return self.state.deribit.btc_mark_usd * self.state.usd_pln

    @property
    def inventory_parameter(self):
        balances = self.state.bitclude.account_info.balances
        total_pln = balances["PLN"].active + balances["PLN"].inactive
        total_btc = balances["BTC"].active + balances["BTC"].inactive

        total_btc_value_in_pln = calculate_btc_value_in_pln(total_btc, self.ref)
        return calculate_inventory_parameter(total_pln, total_btc_value_in_pln)

    @property
    def delta_adjusted_for_inventory(self):
        return calculate_delta_adjusted_for_inventory(self.inventory_parameter)
