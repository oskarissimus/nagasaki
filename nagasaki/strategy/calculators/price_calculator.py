import abc

from nagasaki.enums.common import MarketEnum, SideTypeEnum
from nagasaki.state import State


class PriceCalculator(abc.ABC):
    @abc.abstractmethod
    def calculate(self, state: State, side: SideTypeEnum, asset_symbol: MarketEnum):
        pass
