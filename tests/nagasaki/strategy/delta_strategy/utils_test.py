from decimal import Decimal

import pytest

from nagasaki.strategy.delta_strategy.utils import (
    Line,
    Point,
)


@pytest.mark.parametrize(
    "p1x, p1y, p2x, p2y, a, b",
    [
        ("0", "0", "1", "1", "1", "0"),
        ("0", "0", "1", "0", "0", "0"),
        ("-1", "0.009", "1", "0.002", "-0.0035", "0.0055"),
    ],
)
def test_line_from_points(p1x, p1y, p2x, p2y, a, b):
    p1 = Point(Decimal(p1x), Decimal(p1y))
    p2 = Point(Decimal(p2x), Decimal(p2y))
    line = Line.from_points(p1, p2)
    assert line.a == Decimal(a)
    assert line.b == Decimal(b)
