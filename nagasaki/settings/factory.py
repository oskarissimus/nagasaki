from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.settings.runtime import CalculatorSettings, MarketMakingStrategySettings
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy import calculators
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy

CALCULATOR_TYPE_MAP = {
    "delta": calculators.DeltaCalculator,
    "epsilon": calculators.EpsilonCalculator,
}


def calculator_factory(settings: CalculatorSettings) -> calculators.PriceCalculator:
    Calculator = CALCULATOR_TYPE_MAP[settings.calculator_type]
    return Calculator(**settings.params)


def market_making_strategy_factory(
    settings: MarketMakingStrategySettings,
    bitclude_state: BitcludeState,
    deribit_state: DeribitState,
    yahoo_finance_state: YahooFinanceState,
    dispatcher: StrategyOrderDispatcher,
):
    calculators = [
        calculator_factory(calculator_settings)
        for calculator_settings in settings.calculator_settings
    ]
    return MarketMakingStrategy(
        dispatcher=dispatcher,
        side=SideTypeEnum(settings.side.upper()),
        instrument=InstrumentTypeEnum.from_str(settings.instrument),
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        calculators=calculators,
    )
