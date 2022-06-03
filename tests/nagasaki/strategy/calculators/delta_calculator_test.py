from decimal import Decimal

import pytest

from nagasaki.enums.common import SideTypeEnum
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator


@pytest.mark.parametrize(
    "delta_1, delta_2, side, price, inventory_parameter, expected_price",
    [
        (
            Decimal("0.009"),
            Decimal("0.002"),
            SideTypeEnum.ASK,
            Decimal("1000"),
            Decimal("-1"),
            Decimal("1009"),
        ),
        (
            Decimal("0.009"),
            Decimal("0.002"),
            SideTypeEnum.ASK,
            Decimal("1000"),
            Decimal("1"),
            Decimal("1002"),
        ),
        (
            Decimal("0.009"),
            Decimal("0.002"),
            SideTypeEnum.BID,
            Decimal("1000"),
            Decimal("-1"),
            Decimal("991"),
        ),
        (
            Decimal("0.009"),
            Decimal("0.002"),
            SideTypeEnum.BID,
            Decimal("1000"),
            Decimal("1"),
            Decimal("998"),
        ),
    ],
)
def test_should_calculate(
    delta_1, delta_2, side, price, inventory_parameter, expected_price
):
    calculator = DeltaCalculator(delta_1, delta_2)

    calculated_price = calculator.calculate(
        price, side, inventory_parameter=inventory_parameter
    )

    assert calculated_price == expected_price


@pytest.mark.parametrize(
    "delta_1, delta_2",
    [
        (Decimal("-0.01"), Decimal("0.01")),
        (Decimal("0.01"), Decimal("-0.01")),
        (Decimal("-0.01"), Decimal("-0.01")),
    ],
)
def test_should_raise_for_negative_delta(delta_1, delta_2):
    with pytest.raises(AssertionError):
        DeltaCalculator(delta_1, delta_2)


@pytest.mark.parametrize(
    "inventory_parameter",
    [
        (Decimal("-1.01")),
        (Decimal("1.01")),
    ],
)
def test_should_raise_for_incorrect_inventory_param(inventory_parameter):
    calculator = DeltaCalculator(Decimal(0), Decimal(0))

    with pytest.raises(AssertionError):
        calculator.calculate(
            Decimal("100"), SideTypeEnum.ASK, inventory_parameter=inventory_parameter
        )
