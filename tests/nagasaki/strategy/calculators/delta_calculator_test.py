from collections import defaultdict
from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.enums.common import SideTypeEnum, MarketEnum
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.strategy.calculators.delta_calculator import (
    DeltaCalculator,
    calculate_inventory_parameter,
)


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
    state = mock.Mock()
    state.deribit.mark_price = defaultdict()
    state.deribit.mark_price["BTC"] = price
    state.usd_pln = 1
    calculator = DeltaCalculator(delta_1, delta_2)

    with mock.patch(
        "nagasaki.strategy.calculators.delta_calculator"
        ".DeltaCalculator.inventory_parameter"
    ) as patched_inv_parameter:
        patched_inv_parameter.return_value = inventory_parameter
        calculated_price = calculator.calculate(state, side, MarketEnum.BTC)

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
        calculator = DeltaCalculator(delta_1, delta_2)
        calculator.delta_1
        calculator.delta_2


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
        calculator.inventory_adjusted_delta(inventory_parameter=inventory_parameter)


def test_should_load_deltas_from_config():
    runtime_config = RuntimeConfig()

    with open(runtime_config.path, "w", encoding="utf-8") as file:
        file.write(f"delta_when_pln_only: 0.1\n" f"delta_when_btc_only: 0.2\n")

    calculator = DeltaCalculator()

    assert calculator.delta_1 == Decimal("0.1")
    assert calculator.delta_2 == Decimal("0.2")

    with open(runtime_config.path, "w", encoding="utf-8") as file:
        file.write(f"delta_when_pln_only: 0.3\n" f"delta_when_btc_only: 0.4\n")

    assert calculator.delta_1 == Decimal("0.3")
    assert calculator.delta_2 == Decimal("0.4")


@pytest.mark.parametrize(
    "inventory_parameter, delta",
    [
        (Decimal("0"), Decimal("0.0055")),
        (Decimal("1"), Decimal("0.002")),
        (Decimal("-1"), Decimal("0.009")),
        (Decimal("0.5"), Decimal("0.00375")),
    ],
)
def test_should_adjust_for_inventory(inventory_parameter, delta):
    calculator = DeltaCalculator(Decimal("0.009"), Decimal("0.002"))
    assert calculator.inventory_adjusted_delta(inventory_parameter) == delta


@pytest.mark.parametrize(
    "total_pln, total_btc_value_in_pln, inventory_parameter",
    [
        (100, 0, -1),
        (0, 100, 1),
        (30, 90, 0.5),
        (90, 90, 0),
    ],
)
def test_inventory_parameter(total_pln, total_btc_value_in_pln, inventory_parameter):
    assert (
        calculate_inventory_parameter(total_pln, total_btc_value_in_pln)
        == inventory_parameter
    )
