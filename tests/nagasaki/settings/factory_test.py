from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.settings.factory import (
    calculator_factory,
    hedging_strategy_factory,
    market_making_strategy_factory,
)
from nagasaki.settings.runtime import (
    CalculatorSettings,
    HedgingStrategySettings,
    MarketMakingStrategySettings,
)
from nagasaki.strategy import calculators
from nagasaki.strategy.calculators import EpsilonCalculator


def test_should_create_delta_calculator():
    config = CalculatorSettings(
        calculator_type="delta",
        params={"delta_inv_param_min": "0.6", "delta_inv_param_max": "0.9"},
    )

    calculator = calculator_factory(config)

    assert isinstance(calculator, calculators.DeltaCalculator)
    assert calculator.delta_inv_param_min == Decimal("0.6")
    assert calculator.delta_inv_param_max == Decimal("0.9")


def test_should_create_epsilon_calculator():
    config = CalculatorSettings(calculator_type="epsilon", params={"epsilon": "0.69"})

    calculator = calculator_factory(config)

    assert isinstance(calculator, EpsilonCalculator)
    assert calculator.epsilon == Decimal("0.69")


def test_should_create_delta_epsilon_bid_btc_strategy():
    calculator_configs = [
        CalculatorSettings(calculator_type="epsilon", params={"epsilon": "0.69"}),
        CalculatorSettings(
            calculator_type="delta",
            params={"delta_inv_param_min": "0.6", "delta_inv_param_max": "0.9"},
        ),
    ]
    bitclude_client = mock.Mock()
    bitclude_state = mock.Mock()
    deribit_state = mock.Mock()
    yahoo_state = mock.Mock()
    database = mock.Mock()

    config = MarketMakingStrategySettings(
        side="bid",
        instrument="btc_pln",
        calculator_settings=calculator_configs,
    )

    strategy = market_making_strategy_factory(
        config,
        bitclude_client,
        bitclude_state,
        deribit_state,
        yahoo_state,
        database,
    )

    assert strategy.side == SideTypeEnum.BID
    assert strategy.instrument == InstrumentTypeEnum.BTC_PLN
    assert strategy.bitclude_state is bitclude_state
    assert strategy.deribit_state is deribit_state
    assert strategy.yahoo_finance_state is yahoo_state
    assert strategy.dispatcher.client is bitclude_client
    assert strategy.dispatcher.bitclude_state is bitclude_state
    assert strategy.database is database
    assert len(strategy.calculators) == 2


def test_should_create_hedging_strategy_eth():
    client = mock.Mock()
    bitclude_state = mock.Mock()
    deribit_state = mock.Mock()
    yahoo_state = mock.Mock()
    database = mock.Mock()
    grand_total_delta_max = "0.001"
    grand_total_delta_min = "-0.001"

    config = HedgingStrategySettings(
        instrument="eth_perpetual",
        grand_total_delta_max=grand_total_delta_max,
        grand_total_delta_min=grand_total_delta_min,
    )

    strategy = hedging_strategy_factory(
        config, client, bitclude_state, deribit_state, yahoo_state, database
    )

    assert strategy.instrument == InstrumentTypeEnum.ETH_PERPETUAL
    assert strategy.client is client
    assert strategy.grand_total_delta_max == Decimal(grand_total_delta_max)
    assert strategy.grand_total_delta_min == Decimal(grand_total_delta_min)
    assert strategy.bitclude_state is bitclude_state
    assert strategy.deribit_state is deribit_state
    assert strategy.yahoo_finance_state is yahoo_state
    assert strategy.database is database
