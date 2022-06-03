from decimal import Decimal

import pytest

from nagasaki.enums.common import SideTypeEnum
from nagasaki.strategy.calculators.epsilon_calculator import EpsilonCalculator


@pytest.mark.parametrize(
    "epsilon, side, price, expected_price",
    [
        (Decimal("0.01"), SideTypeEnum.ASK, Decimal("100"), Decimal("99.99")),
        (Decimal("0.01"), SideTypeEnum.BID, Decimal("100"), Decimal("100.01")),
        (Decimal("0.05"), SideTypeEnum.ASK, Decimal("50"), Decimal("49.95")),
        (Decimal("0.05"), SideTypeEnum.BID, Decimal("50"), Decimal("50.05")),
    ],
)
def test_should_calculate(epsilon, side, price, expected_price):
    calculator = EpsilonCalculator(epsilon=epsilon)

    calculated_price = calculator.calculate(price, side)

    assert calculated_price == expected_price
