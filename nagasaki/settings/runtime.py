from typing import Dict, List, Optional

from pydantic import BaseModel


class CalculatorSettings(BaseModel):
    calculator_type: str
    params: Dict[str, str]


class MarketMakingStrategySettings(BaseModel):
    side: str
    instrument: str
    calculator_settings: List[CalculatorSettings]


class HedgingStrategySettings(BaseModel):
    instrument: str


class StrategySettingsList(BaseModel):
    market_making_strategies: Optional[List[MarketMakingStrategySettings]]
    hedging_strategies: Optional[List[HedgingStrategySettings]]


class RuntimeSettings(BaseModel):
    strategies: StrategySettingsList
