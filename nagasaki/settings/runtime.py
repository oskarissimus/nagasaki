from typing import Dict, List, Optional

from pydantic import BaseModel, BaseSettings
from pydantic_yaml import YamlModel


class CalculatorSettings(BaseModel):
    calculator_type: str
    params: Dict[str, str]


class MarketMakingStrategySettings(BaseModel):
    side: str
    instrument: str
    calculator_settings: List[CalculatorSettings]


class HedgingStrategySettings(BaseModel):
    instrument: str
    grand_total_delta_max: str
    grand_total_delta_min: str


class StrategySettingsList(BaseModel):
    market_making_strategies: Optional[List[MarketMakingStrategySettings]]
    hedging_strategies: Optional[List[HedgingStrategySettings]]


class RuntimeSettings(YamlModel):
    market_making_instrument: str
    hedging_instrument: str
    strategies: StrategySettingsList
