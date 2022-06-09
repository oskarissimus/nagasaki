from typing import Dict, List

from pydantic import BaseModel

from nagasaki.strategy import calculators


class CalculatorSettings(BaseModel):
    calculator_type: str
    params: Dict[str, str]


class StrategySettings(BaseModel):
    calculator: List[CalculatorSettings]


class RuntimeSettings(BaseModel):
    strategies: List[StrategySettings]
