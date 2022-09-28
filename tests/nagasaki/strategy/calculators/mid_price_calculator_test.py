from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.enums.common import SideTypeEnum, Symbol
from nagasaki.strategy.calculators.mid_price_calculator import MidPriceCalculator


@pytest.mark.parametrize(
    "delta, side, price, expected_price",
    [
        (Decimal("0.01"), SideTypeEnum.ASK, Decimal("100"), Decimal("101")),
        (Decimal("0.01"), SideTypeEnum.BID, Decimal("100"), Decimal("99")),
        (Decimal("0.05"), SideTypeEnum.ASK, Decimal("50"), Decimal("52.5")),
        (Decimal("0.05"), SideTypeEnum.BID, Decimal("50"), Decimal("47.5")),
    ],
)
def test_should_calculate(delta, side, price, expected_price):
    bitclude = mock.Mock()
    bitclude.mid_price.return_value = price
    calculator = MidPriceCalculator(delta=delta)

    calculated_price = calculator.calculate(
        side, bitclude, None, None, None, orderbook_symbol=Symbol.BTC_PLN
    )

    assert calculated_price == expected_price
