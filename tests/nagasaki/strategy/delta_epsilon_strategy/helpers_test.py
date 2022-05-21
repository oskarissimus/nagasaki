from decimal import Decimal

import pytest

from nagasaki.strategy.delta_epsilon_strategy.ask import (
    calculate_inventory_parameter,
    calculate_delta_adjusted_for_inventory,
)


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


@pytest.mark.parametrize(
    "inventory_parameter, delta",
    [
        (Decimal("0"), Decimal("0.0055")),
        (Decimal("1"), Decimal("0.002")),
        (Decimal("-1"), Decimal("0.009")),
        (Decimal("0.5"), Decimal("0.00375")),
    ],
)
def test_delta_adjusted_for_inventory(inventory_parameter, delta):
    assert calculate_delta_adjusted_for_inventory(inventory_parameter) == delta
