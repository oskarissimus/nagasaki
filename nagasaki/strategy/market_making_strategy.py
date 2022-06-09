from decimal import Decimal
from typing import List

from dependency_injector.wiring import Provide, inject

from nagasaki.clients.base_client import OrderMaker
from nagasaki.containers import Application
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import InstrumentTypeEnum, MarketEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.calculators.price_calculator import PriceCalculator
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher


def make_order(
    price: Decimal, amount: Decimal, side: SideTypeEnum, instrument: InstrumentTypeEnum
) -> OrderMaker:
    return OrderMaker(
        side=side,
        price=price,
        amount=amount,
        instrument=instrument,
    )


class MarketMakingStrategy(AbstractStrategy):
    def __init__(
        self,
        dispatcher: StrategyOrderDispatcher,
        side: SideTypeEnum,
        instrument: InstrumentTypeEnum,
        calculators: List[PriceCalculator] = None,
    ):
        self.dispatcher = dispatcher
        self.calculators = calculators or []
        self.side = side
        self.instrument = instrument
        self.best_price = None
        self.state = None

    @inject
    def execute(self, state: State = Provide[Application.states.state]):
        self.state = state
        self.calculate_best_price()

        order = make_order(self.best_price, self.amount, self.side, self.instrument)

        self.dispatcher.dispatch(order)
        write_order_maker_to_db(order)

    def calculate_best_price(self):
        all_prices = [
            calculator.calculate(self.side, self.asset, self.state)
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
