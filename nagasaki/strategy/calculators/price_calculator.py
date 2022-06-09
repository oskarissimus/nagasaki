import abc

from nagasaki.enums.common import MarketEnum, SideTypeEnum
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState


class PriceCalculator(abc.ABC):
    @abc.abstractmethod
    def calculate(
        self,
        side: SideTypeEnum,
        asset_symbol: MarketEnum,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
    ):
        pass
