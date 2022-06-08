from nagasaki.settings.runtime import CalculatorSettings
from nagasaki.strategy import calculators

CALCULATOR_TYPE_MAP = {
    "delta": calculators.DeltaCalculator,
    "epsilon": calculators.EpsilonCalculator,
}


def calculator_factory(settings: CalculatorSettings) -> calculators.PriceCalculator:
    Calculator = CALCULATOR_TYPE_MAP[settings.calculator_type]
    return Calculator(**settings.params)
