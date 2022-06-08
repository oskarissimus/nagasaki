from typing import Dict, List

from pydantic import BaseModel

from nagasaki.strategy import calculators


class CalculatorSettings(BaseModel):
    calculator_type: str
    params: Dict[str, str]

    def to_calculator(self) -> calculators.PriceCalculator:
        Calculator = self.CALCULATOR_TYPE_MAP[self.calculator_type]
        return Calculator(**self.params)


class StrategySettings(BaseModel):
    calculator: List[CalculatorSettings]


class RuntimeSettings(BaseModel):
    strategies: List[StrategySettings]
