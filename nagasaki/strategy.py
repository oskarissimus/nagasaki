from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.schemas.bitclude import Action, BitcludeOrder
from nagasaki.state import State


class Strategy(ABC):
    @abstractmethod
    def get_actions_bid(self):
        pass

    @abstractmethod
    def get_actions_ask(self):
        pass


class BitcludeEpsilonStrategy(Strategy):
    """
    Bid top BID + EPSILON
    Bid top ASK - EPSILON
    """

    def __init__(self, state: State):
        self.EPSILON = Decimal("2.137")
        self.ASK_TRIGGER = Decimal("0.004")
        self.BID_TRIGGER = Decimal("0.004")
        self.state = state

    def get_actions_bid(self) -> List[Action]:
        logger.info("CIPSKO")

        price = self.state.get_top_bid() + self.EPSILON
        amount = self.state.bitclude_account_info.balances["PLN"].active / price
        action_bid_over = Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(side=SideTypeEnum.BID, price=price, amount=amount),
        )
        own_bid = self.state.get_own_bid_max()
        action_cancel = Action(action_type=ActionTypeEnum.CANCEL, order=own_bid)
        action_noop = Action(action_type=ActionTypeEnum.NOOP)

        if self.bidding_is_profitable():
            if own_bid is None:
                return [action_bid_over]
            else:
                return [action_cancel, action_bid_over]
        else:
            if own_bid is None:
                return [action_noop]
            else:
                return [action_cancel]

    def get_actions_ask(self):
        pass

    def bidding_is_profitable(self) -> bool:
        MARK = self.state.btc_mark_usd * self.state.usd_pln
        TOP_BID = self.state.get_top_bid()
        logger.info(f"{(MARK - (TOP_BID + self.EPSILON)) / MARK=}")
        return (MARK - (TOP_BID + self.EPSILON)) / MARK > self.BID_TRIGGER

    def print_state(self):
        print(self.state.bid_orderbook, self.state.ask_orderbook)
