from decimal import Decimal

from nagasaki.enums.common import SideTypeEnum
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.strategy.calculators.price_calculator import PriceCalculator


class EpsilonCalculator(PriceCalculator):
    def __init__(self, epsilon: Decimal):
        self.epsilon = epsilon

    def calculate(self, state: State, side: SideTypeEnum) -> Decimal:
        if side == SideTypeEnum.ASK:
            epsilon_price = self.calculate_ask(state.bitclude.top_ask())
        else:
            epsilon_price = self.calculate_bid(state.bitclude.top_bid())
        logger.info(f"{epsilon_price=:.0f}")
        return epsilon_price

    def calculate_ask(self, price):
        return price - self.epsilon

    def calculate_bid(self, price):
        return price + self.epsilon
