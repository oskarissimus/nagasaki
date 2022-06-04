from decimal import Decimal
from typing import List

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum, MarketEnum
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
        side: SideTypeEnum,
        instrument: InstrumentTypeEnum,
        calculators: List[PriceCalculator] = None,
    ):
        self.state = state
        self.dispatcher = dispatcher
        self.calculators = calculators or []
        self.side = side
        self.instrument = instrument
        self.best_price = None

    def execute(self):
        self.calculate_best_price()

        order = make_order(self.best_price, self.amount, self.side)

        self.dispatcher.dispatch(order)
        write_order_maker_to_db(order)

    def calculate_best_price(self):
        all_prices = [
            calculator.calculate(self.state, self.side, self.asset)
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
            return self.total_assets
        return self.total_pln / self.best_price

    @property
    def total_assets(self):
        return (
            self.state.bitclude.account_info.balances[self.asset].active
            + self.state.bitclude.account_info.balances[self.asset].inactive
        )

    @property
    def total_pln(self):
        return (
            self.state.bitclude.account_info.balances["PLN"].active
            + self.state.bitclude.account_info.balances["PLN"].inactive
        )

    @property
    def asset(self):
        return MarketEnum(self.instrument.market_1)
