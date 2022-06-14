from decimal import Decimal

from nagasaki.enums.common import Currency, MarketEnum, SideTypeEnum, Symbol
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.calculators.price_calculator import PriceCalculator


class EpsilonCalculator(PriceCalculator):
    def __init__(self, epsilon: str):
        self.epsilon = Decimal(epsilon) or Decimal("0.01")

    def calculate(
        self,
        side: SideTypeEnum,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        currency: Currency = None,
        orderbook_symbol: Symbol = None,
    ) -> Decimal:
        if side == SideTypeEnum.ASK:
            epsilon_price = self.calculate_ask(
                bitclude_state.top_ask(orderbook_symbol.value)
            )
        else:
            epsilon_price = self.calculate_bid(
                bitclude_state.top_bid(orderbook_symbol.value)
            )
        logger.info(f"{epsilon_price=:.0f}")
        return epsilon_price

    def calculate_ask(self, price):
        return price - self.epsilon

    def calculate_bid(self, price):
        return price + self.epsilon
