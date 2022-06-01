from dataclasses import dataclass
from decimal import Decimal

from nagasaki.strategy.abstract_strategy import StrategyException


@dataclass
class Point:
    # pylint: disable=invalid-name
    x: Decimal
    y: Decimal


@dataclass
class Line:
    # pylint: disable=invalid-name
    a: Decimal
    b: Decimal

    @classmethod
    def from_points(cls, p1: Point, p2: Point):
        a = (p2.y - p1.y) / (p2.x - p1.x)
        b = p1.y - a * p1.x
        return cls(a, b)

    def calculate_y(self, x):
        return self.a * x + self.b


def calculate_btc_value_in_pln(btc: Decimal, price: Decimal) -> Decimal:
    return btc * price


def calculate_inventory_parameter(
    total_pln: Decimal, total_btc_value_in_pln: Decimal
) -> Decimal:
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1


def calculate_delta_adjusted_for_inventory(
    inventory_parameter, line: Line = None
):  # pylint: disable=invalid-name
    line = line or Line(Decimal("-0.0035"), Decimal("0.0055"))
    res = line.calculate_y(inventory_parameter)
    if res <= 0:
        raise StrategyException(f"Delta is too small for inventory parameter: {res}")
    return res
