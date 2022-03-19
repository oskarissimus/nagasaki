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
        self.delta = Decimal("0.005")

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

    def get_actions_ask(self) -> List[Action]:
        top_ask = self.get_top_ask()
        total_btc = self.get_total_btc()
        ref = self.get_ref()

        delta_price = ref * (1 + self.delta)
        epsilon_price = top_ask - self.epsilon

        desirable_price = max(delta_price, epsilon_price)
        logger.info(f"{delta_price=:.2f} {epsilon_price=:.2f}")
        desirable_amount = total_btc

        actions = self.cancel_all_asks()

        desirable_action = self.ask_action(desirable_price, desirable_amount)
        actions.append(desirable_action)

        return actions
