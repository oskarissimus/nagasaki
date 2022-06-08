from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Balance
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.calculators.epsilon_calculator import EpsilonCalculator
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy


@pytest.fixture(name="initialized_state")
def fixture_initialized_state():
    btc_price_deribit = 40_000
    usd_pln = 4

    active_plns = 100_000
    active_btcs = 1

    state = State()
    state.deribit = DeribitState()
    state.deribit.mark_price["BTC"] = Decimal(btc_price_deribit)
    state.yahoo = YahooFinanceState()
    state.yahoo.usd_pln = Decimal(usd_pln)
    state.bitclude = BitcludeState()
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(active=Decimal(active_btcs), inactive=Decimal("0")),
        }
    )
    return state


@pytest.fixture(name="dispatcher")
def fixture_dispatcher():
    return mock.Mock()


@pytest.fixture(name="delta_calculator")
def fixture_delta_calculator():
    return DeltaCalculator(Decimal("0.009"), Decimal("0.002"))


@pytest.fixture(name="epsilon_calculator")
def fixture_epsilon_calculator():
    return EpsilonCalculator(Decimal("0.01"))


@pytest.fixture(name="strategy_ask")
def fixture_strategy_ask(
    initialized_state, dispatcher, delta_calculator, epsilon_calculator
):
    calculators = [delta_calculator, epsilon_calculator]
    return MarketMakingStrategy(
        initialized_state,
        dispatcher,
        calculators=calculators,
        side=SideTypeEnum.ASK,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


@pytest.fixture(name="strategy_bid")
def fixture_strategy_bid(
    initialized_state, dispatcher, delta_calculator, epsilon_calculator
):
    calculators = [delta_calculator, epsilon_calculator]
    return MarketMakingStrategy(
        initialized_state,
        dispatcher,
        calculators=calculators,
        side=SideTypeEnum.BID,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )
