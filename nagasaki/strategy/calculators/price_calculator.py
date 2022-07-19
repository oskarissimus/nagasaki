import abc
from decimal import Decimal
from typing import Optional

from nagasaki.enums.common import Currency, MarketEnum, SideTypeEnum, Symbol
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState


class PriceCalculator(abc.ABC):
    @abc.abstractmethod
    def calculate(
        self,
        side: SideTypeEnum,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        currency: Optional[Currency],
        orderbook_symbol: Optional[Symbol],
    ) -> Decimal:
        pass
