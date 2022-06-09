from typing import Dict, List

from pydantic import BaseModel


class CalculatorSettings(BaseModel):
    calculator_type: str
    params: Dict[str, str]


class MarketMakingStrategySettings(BaseModel):
    side: str
    instrument: str
    calculator_settings: List[CalculatorSettings]


class RuntimeSettings(BaseModel):
    market_making_strategies: List[MarketMakingStrategySettings]
