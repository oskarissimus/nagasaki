from decimal import Decimal

from nagasaki.clients import BaseClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.database.database import Database
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum, Symbol
from nagasaki.settings.runtime import (
    CalculatorSettings,
    HedgingStrategySettings,
    MarketMakingStrategySettings,
)
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState
from nagasaki.strategy import calculators
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy.hedging_strategy import HedgingStrategy
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
    client: BaseClient,
    state: State,
    bitclude_state: BitcludeState,
    deribit_state: DeribitState,
    yahoo_finance_state: YahooFinanceState,
):
    calculators = [
        calculator_factory(calculator_settings)
        for calculator_settings in settings.calculator_settings
    ]
    dispatcher = StrategyOrderDispatcher(client=client, bitclude_state=bitclude_state)
    return MarketMakingStrategy(
        dispatcher=dispatcher,
        side=SideTypeEnum(settings.side.upper()),
        instrument=InstrumentTypeEnum.from_str(settings.instrument),
        symbol=Symbol(settings.symbol),
        state=state,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        calculators=calculators,
    )


def hedging_strategy_factory(
    settings: HedgingStrategySettings,
    client: BaseClient,
    state: State,
    bitclude_state: BitcludeState,
    deribit_state: DeribitState,
    yahoo_finance_state: YahooFinanceState,
):
    return HedgingStrategy(
        client=client,
        instrument=InstrumentTypeEnum.from_str(settings.instrument),
        symbol=Symbol(settings.symbol),
        grand_total_delta_max=Decimal(settings.grand_total_delta_max),
        grand_total_delta_min=Decimal(settings.grand_total_delta_min),
        state=state,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
    )


def create_strategies(
    database: Database,
    bitclude_client: BaseClient,
    deribit_client: DeribitClient,
    state: State,
    bitclude_state: BitcludeState,
    deribit_state: DeribitState,
    yahoo_finance_state: YahooFinanceState,
):
    strategy_settings = database.get_newest_settings().strategies
    strategies = []

    for mm_settings in strategy_settings.market_making_strategies or ():
        strategies.append(
            market_making_strategy_factory(
                mm_settings,
                bitclude_client,
                state,
                bitclude_state,
                deribit_state,
                yahoo_finance_state,
            )
        )

    for hedging_settings in strategy_settings.hedging_strategies or ():
        strategies.append(
            hedging_strategy_factory(
                hedging_settings,
                deribit_client,
                state,
                bitclude_state,
                deribit_state,
                yahoo_finance_state,
            )
        )

    return strategies
