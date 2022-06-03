from decimal import Decimal

import pytest

from nagasaki.strategy.market_making_strategy import calculate_inventory_parameter


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
