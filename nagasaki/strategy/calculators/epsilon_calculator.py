from decimal import Decimal

from nagasaki.enums.common import MarketEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.strategy.calculators.price_calculator import PriceCalculator


class EpsilonCalculator(PriceCalculator):
    def __init__(self, epsilon: Decimal):
        self.epsilon = epsilon

    def calculate(
        self, state: State, side: SideTypeEnum, asset_symbol: MarketEnum
    ) -> Decimal:
        if side == SideTypeEnum.ASK:
            epsilon_price = self.calculate_ask(state.bitclude.top_ask(asset_symbol))
        else:
            epsilon_price = self.calculate_bid(state.bitclude.top_bid(asset_symbol))
        logger.info(f"{epsilon_price=:.0f}")
        return epsilon_price

    def calculate_ask(self, price):
        return price - self.epsilon

    def calculate_bid(self, price):
        return price + self.epsilon
