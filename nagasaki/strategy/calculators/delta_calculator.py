from decimal import Decimal

from nagasaki.enums.common import SideTypeEnum


class DeltaCalculator:
    def __init__(self, delta_1: Decimal, delta_2: Decimal):
        assert delta_1 >= 0
        assert delta_2 >= 0
        self.delta_1 = delta_1
        self.delta_2 = delta_2

    def calculate(
        self, price: Decimal, side: SideTypeEnum, inventory_parameter: Decimal
    ):
        if side == SideTypeEnum.ASK:
            return self.calculate_ask(price, inventory_parameter)
        if side == SideTypeEnum.BID:
            return self.calculate_bid(price, inventory_parameter)

    def calculate_ask(self, price, inventory_parameter):
        return price * (1 + self.inventory_adjusted_delta(inventory_parameter))

    def calculate_bid(self, price, inventory_parameter):
        return price * (1 - self.inventory_adjusted_delta(inventory_parameter))

    def inventory_adjusted_delta(self, inventory_parameter):
        """
        delta(inventory_parameter) is a linear function with two
        known points: (-1, delta_1) and (1, delta_2)

        as inv_param goes from -1 to 1 (changes by 2), delta changes by
        delta_x - delta_1:
        (inv_param - (-1)/(1-(-1)) = (delta_x - delta_1)/(delta_2 - delta_1)
        (inv_param + 1)/2 = (delta_x - delta_1)/(delta_2 - delta_1)

        solving for delta_x:
        delta_x = delta_1 + (delta_2 - delta_1) * (inv_param + 1)/2

        """
        assert inventory_parameter >= Decimal("-1")
        assert inventory_parameter <= Decimal("1")

        return self.delta_1 + ((inventory_parameter + 1) / 2) * (
            self.delta_2 - self.delta_1
        )
