from decimal import Decimal
from typing import List

from nagasaki.clients.bitclude.dto import AmmountTooLowError
from nagasaki.enums.common import (
    Currency,
    InstrumentTypeEnum,
    MarketEnum,
    SideTypeEnum,
    Symbol,
)
from nagasaki.exceptions import SkippableStrategyException
from nagasaki.logger import logger
from nagasaki.models.bitclude import OrderMaker
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.calculators.price_calculator import PriceCalculator
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.utils.common import round_decimals_down


def make_order(
    price: Decimal,
    amount: Decimal,
    side: SideTypeEnum,
    instrument: InstrumentTypeEnum,
    hidden: bool,
    symbol: Symbol,
) -> OrderMaker:
    return OrderMaker(
        side=side,
        price=price,
        symbol=symbol,
        amount=amount,
        instrument=instrument,
        hidden=hidden,
    )


class MarketMakingStrategy(AbstractStrategy):
    def __init__(
        self,
        dispatcher: StrategyOrderDispatcher,
        side: SideTypeEnum,
        instrument: InstrumentTypeEnum,
        symbol: Symbol,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        calculators: List[PriceCalculator] = None,
    ):
        self.dispatcher = dispatcher
        self.side = side
        self.instrument = instrument
        self.symbol = symbol
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state
        self.calculators = calculators or []
        self.best_price = None

    def execute(self) -> OrderMaker:
        self.calculate_best_price()

        if self.amount == 0:
            return None

        order = make_order(
            self.best_price,
            self.amount,
            self.side,
            self.instrument,
            hidden=False,
            symbol=self.symbol,
        )

        try:
            self.dispatcher.dispatch(order)
        except AmmountTooLowError as error:
            raise SkippableStrategyException from error
        return order

    def calculate_best_price(self):
        all_prices = [
            calculator.calculate(
                self.side,
                self.bitclude_state,
                self.deribit_state,
                self.yahoo_finance_state,
                currency=self.currency,
                orderbook_symbol=self.symbol,
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
        return round_decimals_down(self.total_pln / self.best_price, 4)

    @property
    def total_assets(self):
        return (
            self.bitclude_state.account_info.balances[self.currency].active
            + self.bitclude_state.account_info.balances[self.currency].inactive
        )

    @property
    def total_pln(self):
        return (
            self.bitclude_state.account_info.balances["PLN"].active
            + self.bitclude_state.account_info.balances["PLN"].inactive
        )

    @property
    def currency(self):
        return Currency(self.instrument.market_1)
