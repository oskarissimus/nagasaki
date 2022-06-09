from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.settings.factory import calculator_factory, market_making_strategy_factory
from nagasaki.settings.runtime import CalculatorSettings, MarketMakingStrategySettings
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


def test_should_create_delta_epsilon_bid_btc_strategy():
    calculator_configs = [
        CalculatorSettings(calculator_type="epsilon", params={"epsilon": "0.69"}),
        CalculatorSettings(
            calculator_type="delta", params={"delta_1": "0.6", "delta_2": "0.9"}
        ),
    ]
    dispatcher = mock.Mock()
    bitclude_state = mock.Mock()
    deribit_state = mock.Mock()
    yahoo_state = mock.Mock()

    config = MarketMakingStrategySettings(
        side="bid",
        instrument="btc_pln",
        calculator_settings=calculator_configs,
    )

    strategy = market_making_strategy_factory(
        config,
        bitclude_state,
        deribit_state,
        yahoo_state,
        dispatcher=dispatcher,
    )

    assert strategy.side == SideTypeEnum.BID
    assert strategy.instrument == InstrumentTypeEnum.BTC_PLN
    assert strategy.bitclude_state is bitclude_state
    assert strategy.deribit_state is deribit_state
    assert strategy.yahoo_finance_state is yahoo_state
    assert strategy.dispatcher is dispatcher
    assert len(strategy.calculators) == 2
