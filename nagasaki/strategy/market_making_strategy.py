from decimal import Decimal
from typing import List

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.database import Database
from nagasaki.enums.common import InstrumentTypeEnum, MarketEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
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
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        database: Database,
        calculators: List[PriceCalculator] = None,
    ):
        self.dispatcher = dispatcher
        self.side = side
        self.instrument = instrument
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state
        self.calculators = calculators or []
        self.database = database
        self.best_price = None

    def execute(self):
        self.calculate_best_price()

        order = make_order(self.best_price, self.amount, self.side, self.instrument)

        self.dispatcher.dispatch(order)
        self.database.save_order(order)

    def calculate_best_price(self):
        all_prices = [
            calculator.calculate(
                self.side,
                self.asset,
                self.bitclude_state,
                self.deribit_state,
                self.yahoo_finance_state,
            )
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
            self.bitclude_state.account_info.balances[self.asset].active
            + self.bitclude_state.account_info.balances[self.asset].inactive
        )

    @property
    def total_pln(self):
        return (
            self.bitclude_state.account_info.balances["PLN"].active
            + self.bitclude_state.account_info.balances["PLN"].inactive
        )

    @property
    def asset(self):
        return MarketEnum(self.instrument.market_1)
