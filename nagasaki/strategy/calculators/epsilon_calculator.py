from decimal import Decimal

from nagasaki.enums.common import SideTypeEnum


class EpsilonCalculator:
    def __init__(self, epsilon: Decimal):
        self.epsilon = epsilon

    def calculate(self, price: Decimal, side: SideTypeEnum) -> Decimal:
        if side == SideTypeEnum.ASK:
            return self.calculate_ask(price)
        if side == SideTypeEnum.BID:
            return self.calculate_bid(price)

    def calculate_ask(self, price):
        return price - self.epsilon

    def calculate_bid(self, price):
        return price + self.epsilon
