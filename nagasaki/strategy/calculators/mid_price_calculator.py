from decimal import Decimal
from typing import Optional

from nagasaki.enums.common import Currency, SideTypeEnum, Symbol
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.calculators.price_calculator import PriceCalculator


class MidPriceCalculator(PriceCalculator):
    def __init__(self, delta: str):
        self.delta = Decimal(delta) or Decimal("0.03")

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
            delta_mid_price = self.calculate_ask(
                bitclude_state.mid_price(orderbook_symbol.value)
            )
        else:
            delta_mid_price = self.calculate_bid(
                bitclude_state.mid_price(orderbook_symbol.value)
            )
        logger.info(f"{delta_mid_price=:.0f}")
        return Decimal(delta_mid_price)

    def calculate_ask(self, price):
        return price * (1 + self.delta)

    def calculate_bid(self, price):
        return price * (1 - self.delta)
