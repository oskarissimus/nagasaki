from decimal import Decimal
from typing import List

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.calculators.price_calculator import PriceCalculator
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.state import State
from nagasaki.logger import logger


def make_order(price: Decimal, amount: Decimal, side: SideTypeEnum) -> OrderMaker:
    return OrderMaker(
        side=side,
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


class MarketMakingStrategy(AbstractStrategy):
    def __init__(
        self,
        state: State,
        dispatcher: StrategyOrderDispatcher,
        side: SideTypeEnum = None,
        calculators: List[PriceCalculator] = None,
    ):
        self.state = state
        self.dispatcher = dispatcher
        self.calculators = calculators or []
        self.side = side
        self.best_price = None

    def execute(self):
        self.calculate_best_price()

        order = make_order(self.best_price, self.amount, self.side)

        self.dispatcher.dispatch(order)
        write_order_maker_to_db(order)

    def calculate_best_price(self):
        all_prices = [
            calculator.calculate(self.state, self.side)
            for calculator in self.calculators
        ]
        self.best_price = self.best(all_prices)
        logger.info(f"{self.best_price=:.0f}")

    @property
    def best(self):
        return max if self.side == SideTypeEnum.ASK else min

    @property
    def amount(self):
        if self.side == SideTypeEnum.ASK:
            return self.total_btc
        return self.total_pln / self.best_price

    @property
    def total_btc(self):
        return (
            self.state.bitclude.account_info.balances["BTC"].active
            + self.state.bitclude.account_info.balances["BTC"].inactive
        )

    @property
    def total_pln(self):
        return (
            self.state.bitclude.account_info.balances["PLN"].active
            + self.state.bitclude.account_info.balances["PLN"].inactive
        )
