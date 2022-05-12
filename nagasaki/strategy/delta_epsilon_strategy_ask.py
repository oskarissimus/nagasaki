from decimal import Decimal
from typing import List
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
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


class DeltaEpsilonStrategyAsk(AbstractStrategy):
    def __init__(self, state: State):
        self.state = state
        self.epsilon = Decimal("0.01")
        self.price_tolerance = Decimal("100")
        self.amount_tolerance = Decimal("0.000_3")

    def get_actions(self) -> List[Action]:
        delta_price = calculate_delta_price(self.ref, self.delta_adjusted_for_inventory)
        epsilon_price = calculate_epsilon_price(self.top_ask, self.epsilon)

        desirable_price = max(delta_price, epsilon_price)
        desirable_amount = self.total_btc
        desirable_action = self.ask_action(desirable_price, desirable_amount)

        active_offers = self.state.bitclude.active_offers

        if len(active_offers) == 0:
            return [desirable_action]

        if len(active_offers) == 1:
            active_offer = active_offers[0]
            if self.active_offer_is_within_tolerance(
                active_offer, desirable_price, desirable_amount
            ):
                return []

        actions = self.cancel_all_asks()
        actions.append(desirable_action)
        return actions

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

    def cancel_all_asks(self):
        actions = []
        asks = [
            offer
            for offer in self.state.bitclude.active_offers
            if offer.offertype == SideTypeEnum.ASK
        ]
        for offer in asks:
            actions.append(
                Action(
                    action_type=ActionTypeEnum.CANCEL_AND_WAIT,
                    order=offer.to_bitclude_order(),
                )
            )
        return actions

    @staticmethod
    def ask_action(price: Decimal, amount: Decimal):
        return Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.ASK,
                price=price,
                amount=amount,
            ),
        )

    def active_offer_is_within_tolerance(
        self,
        active_offer: BitcludeOrder,
        desireable_price: Decimal,
        desireable_amount: Decimal,
    ):
        return (
            abs(active_offer.price - desireable_price) < self.price_tolerance
            and abs(active_offer.amount - desireable_amount) < self.amount_tolerance
        )

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
