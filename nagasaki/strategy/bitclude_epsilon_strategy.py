from decimal import Decimal
from typing import List

from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.models.bitclude import Action, BitcludeOrder
from nagasaki.state import State
from nagasaki.strategy.abstract_strategy import AbstractStrategy


class BitcludeEpsilonStrategy(AbstractStrategy):
    """
    Bid top BID + EPSILON
    Bid top ASK - EPSILON
    """

    def __init__(self, state: State, epsilon: Decimal = Decimal("2.137")):
        self.EPSILON = epsilon
        self.ASK_TRIGGER = Decimal("0.002")
        self.BID_TRIGGER = Decimal("0.002")
        self.state = state

    def get_actions_bid(self) -> List[Action]:
        logger.info("I'm not even trying to bid.")
        return []

    def get_actions_ask(self) -> List[Action]:
        btc_balance = (
            self.state.bitclude.account_info.balances["BTC"].active
            + self.state.bitclude.account_info.balances["BTC"].inactive
        )
        top_ask = self.state.get_top_ask()
        active_offers = self.state.bitclude.active_offers
        price = top_ask - self.EPSILON

        action_ask_over = Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.ASK,
                price=price,
                amount=Decimal(btc_balance),
            ),
        )
        result_actions = []
        if self.asking_is_profitable():
            logger.info("asking is profitable")
            for offer in active_offers:
                result_actions.append(
                    Action(
                        action_type=ActionTypeEnum.CANCEL,
                        order=offer.to_bitclude_order(),
                    )
                )
            result_actions.append(action_ask_over)
        else:
            logger.info("asking is not profitable")
        return result_actions

    def asking_is_profitable(self) -> bool:
        MARK = self.state.deribit.btc_mark_usd * self.state.usd_pln
        TOP_ASK = self.state.get_top_ask()
        ask_profitability = (TOP_ASK - MARK - self.EPSILON) / MARK
        logger.info(f"{ask_profitability=:.4f}")
        return ask_profitability > self.ASK_TRIGGER
