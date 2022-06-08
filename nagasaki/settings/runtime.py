from decimal import Decimal
from functools import cached_property
from typing import Dict, List

from pydantic import BaseModel, BaseSettings

from nagasaki.strategy import calculators


class CalculatorSettings(BaseModel):
    CALCULATOR_TYPE_MAP = {
        "delta": calculators.DeltaCalculator,
        "epsilon": calculators.EpsilonCalculator,
    }

    calculator_type: str
    params: Dict[str, str]

    def to_calculator(self) -> calculators.PriceCalculator:
        Calculator = self.CALCULATOR_TYPE_MAP[self.calculator_type]
        return Calculator(**self.params)


class StrategySettings(BaseModel):
    calculator: List[CalculatorSettings]


class RuntimeSettings(BaseModel):
    strategies: List[StrategySettings]
