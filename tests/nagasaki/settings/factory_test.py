from decimal import Decimal

from nagasaki.settings.factory import calculator_factory
from nagasaki.settings.runtime import CalculatorSettings
from nagasaki.strategy import calculators
from nagasaki.strategy.calculators import EpsilonCalculator


def test_should_create_delta_calculator():
    config = CalculatorSettings(
        calculator_type="delta", params={"delta_1": "0.6", "delta_2": "0.9"}
    )

    calculator = calculator_factory(config)

    assert isinstance(calculator, calculators.DeltaCalculator)
    assert calculator.delta_1 == Decimal("0.6")
    assert calculator.delta_2 == Decimal("0.9")


def test_should_create_epsilon_calculator():
    config = CalculatorSettings(calculator_type="epsilon", params={"epsilon": "0.69"})

    calculator = calculator_factory(config)

    assert isinstance(calculator, EpsilonCalculator)
    assert calculator.epsilon == Decimal("0.69")
