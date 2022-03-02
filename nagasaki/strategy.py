from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List
from nagasaki.clients.trejdoo_client import get_price_usd_pln

from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.models.bitclude import Action, BitcludeOrder
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

    def __init__(self, state: State, epsilon: Decimal = Decimal("2.137")):
        self.EPSILON = epsilon
        self.ASK_TRIGGER = Decimal("0.002")
        self.BID_TRIGGER = Decimal("0.002")
        self.state = state

    def get_actions_bid(self) -> List[Action]:
        logger.info("CIPSKO")
        self.state.usd_pln = get_price_usd_pln()
        price = self.state.get_top_bid() + self.EPSILON
        amount = self.state.bitclude_account_info.balances["PLN"].active / price
        action_bid_over = Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(side=SideTypeEnum.BID, price=price, amount=amount),
        )
        own_bid = self.state.get_own_bid_max()
        action_cancel = Action(action_type=ActionTypeEnum.CANCEL, order=own_bid)
        action_noop = Action(action_type=ActionTypeEnum.NOOP)
        if amount < Decimal("10"):
            return [action_noop]
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
        self.state.usd_pln = get_price_usd_pln()
        btc_balance = self.state.bitclude_account_info.balances["BTC"].active
        top_ask = self.state.get_top_ask()
        own_ask = self.state.get_own_ask_min()
        price = top_ask - self.EPSILON
        action_cancel_ask = Action(action_type=ActionTypeEnum.CANCEL, order=own_ask)
        action_noop = Action(action_type=ActionTypeEnum.NOOP)

        action_ask_over = Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.ASK,
                price=price,
                amount=Decimal(btc_balance),
            ),
        )
        if btc_balance < 0.0001:
            return [action_noop]
        if self.asking_is_profitable():
            if own_ask is None:
                return [action_ask_over]
            else:
                return [action_cancel_ask, action_ask_over]
        else:
            if own_ask is None:
                return [action_noop]
            else:
                return [action_cancel_ask]

    def bidding_is_profitable(self) -> bool:
        print("Executing strategy")
        print(f"{self.state.usd_pln=}")
        MARK = self.state.btc_mark_usd * self.state.usd_pln
        TOP_BID = self.state.get_top_bid()
        logger.info(f"{(MARK - (TOP_BID + self.EPSILON)) / MARK=}")
        bidding_profitability = (MARK - (TOP_BID + self.EPSILON)) / MARK
        print(f"BID PROFITABILITY: {bidding_profitability:.5f}")

        return (MARK - (TOP_BID + self.EPSILON)) / MARK > self.BID_TRIGGER

    def asking_is_profitable(self) -> bool:
        MARK = self.state.btc_mark_usd * self.state.usd_pln
        TOP_ASK = self.state.get_top_ask()
        ask_profitability = (TOP_ASK - MARK - self.EPSILON) / MARK
        print(f"ASK PROFITABILITY:  {ask_profitability:.5f}")
        return ask_profitability > self.ASK_TRIGGER

    def print_state(self):
        pass
        # print(self.state.bid_orderbook, self.state.ask_orderbook)
