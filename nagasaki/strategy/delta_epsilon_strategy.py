from decimal import Decimal
from typing import List
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import Action, BitcludeOrder
from nagasaki.strategy.abstract_strategy import AbstractStrategy, StrategyException
from nagasaki.logger import logger
from nagasaki.state import State


class DeltaEpsilonStrategy(AbstractStrategy):
    def __init__(self, state: State):
        self.state = state
        self.epsilon = Decimal("0.01")
        # self.delta = Decimal("0.003")
        self.price_tolerance = Decimal("100")
        self.amount_tolerance = Decimal("0.000_3")

    def get_actions_bid(self):
        logger.info("I'm not even trying to bid.")
        return []

    def get_top_ask(self):
        return min(self.state.bitclude.orderbook_rest.asks, key=lambda x: x.price).price

    def get_total_btc(self):
        return (
            self.state.bitclude.account_info.balances["BTC"].active
            + self.state.bitclude.account_info.balances["BTC"].inactive
        )

    def get_ref(self):
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

    def ask_action(self, price: Decimal, amount: Decimal):
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

    def get_delta_adjusted_for_inventory(self, inventory_parameter: Decimal):
        A = Decimal("-0.0035")
        B = Decimal("0.0055")
        res = A * inventory_parameter + B
        if res <= 0:
            raise StrategyException(
                f"Delta is too small for inventory parameter: {res}"
            )
        return res

    def get_inventory_parameter(self):
        balances = self.state.bitclude.account_info.balances
        total_pln = balances["PLN"].active + balances["PLN"].inactive
        total_btc = balances["BTC"].active + balances["BTC"].inactive

        btc_mark_price_pln = self.get_ref()

        total_btc_value_in_pln = total_btc * btc_mark_price_pln
        wallet_sum_in_pln = total_pln + total_btc_value_in_pln
        pln_to_sum_ratio = (
            total_btc_value_in_pln / wallet_sum_in_pln
        )  # values from 0 to 1
        return pln_to_sum_ratio * 2 - 1

    def get_actions_ask(self) -> List[Action]:
        top_ask = self.get_top_ask()
        total_btc = self.get_total_btc()
        ref = self.get_ref()

        inventory_parameter = self.get_inventory_parameter()
        logger.info(f"{inventory_parameter=:.3f}")
        delta = self.get_delta_adjusted_for_inventory(inventory_parameter)
        logger.info(f"{delta=:.5f}")
        delta_price = ref * (1 + delta)
        epsilon_price = top_ask - self.epsilon

        desirable_price = max(delta_price, epsilon_price)
        going_for_delta = desirable_price == delta_price
        logger.info(
            f"{delta_price=:.2f} {epsilon_price=:.2f} going for {'delta' if going_for_delta else 'epsilon'}"
        )
        desirable_amount = total_btc

        if len(self.state.bitclude.active_offers) == 0:
            desirable_action = self.ask_action(desirable_price, desirable_amount)
            return [desirable_action]

        elif len(self.state.bitclude.active_offers) == 1:
            active_offer = self.state.bitclude.active_offers[0]
            if self.active_offer_is_within_tolerance(
                active_offer, desirable_price, desirable_amount
            ):
                return []
            else:
                actions = self.cancel_all_asks()
                desirable_action = self.ask_action(desirable_price, desirable_amount)
                actions.append(desirable_action)
                return actions
        else:
            actions = self.cancel_all_asks()
            desirable_action = self.ask_action(desirable_price, desirable_amount)
            actions.append(desirable_action)
            return actions
