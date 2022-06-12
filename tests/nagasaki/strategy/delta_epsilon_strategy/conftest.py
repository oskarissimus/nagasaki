from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Balance
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.calculators.epsilon_calculator import EpsilonCalculator
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy


@pytest.fixture(name="bitclude_state")
def fixture_bitclude_state():
    active_plns = 100_000
    active_btcs = 1

    bitclude = BitcludeState()
    bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(active=Decimal(active_btcs), inactive=Decimal("0")),
        }
    )
    return bitclude


@pytest.fixture(name="deribit_state")
def fixture_deribit_state():
    btc_price_deribit = 40_000

    deribit = DeribitState()
    deribit.mark_price["BTC"] = Decimal(btc_price_deribit)
    return deribit


@pytest.fixture(name="yahoo_finance_state")
def fixture_yahoo_finance_state():
    usd_pln = 4

    yahoo = YahooFinanceState()
    yahoo.usd_pln = Decimal(usd_pln)
    return yahoo


@pytest.fixture(name="dispatcher")
def fixture_dispatcher():
    return mock.Mock()


@pytest.fixture(name="delta_calculator")
def fixture_delta_calculator():
    return DeltaCalculator(Decimal("0.009"), Decimal("0.002"))


@pytest.fixture(name="epsilon_calculator")
def fixture_epsilon_calculator():
    return EpsilonCalculator(Decimal("0.01"))


@pytest.fixture(name="database")
def fixture_database():
    return mock.Mock()


@pytest.fixture(name="strategy_ask")
def fixture_strategy_ask(
    dispatcher,
    delta_calculator,
    epsilon_calculator,
    bitclude_state,
    deribit_state,
    yahoo_finance_state,
    database,
):
    calculators = [delta_calculator, epsilon_calculator]
    return MarketMakingStrategy(
        dispatcher,
        side=SideTypeEnum.ASK,
        instrument=InstrumentTypeEnum.BTC_PLN,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        calculators=calculators,
        database=database,
    )


@pytest.fixture(name="strategy_bid")
def fixture_strategy_bid(
    dispatcher,
    delta_calculator,
    epsilon_calculator,
    bitclude_state,
    deribit_state,
    yahoo_finance_state,
    database,
):
    calculators = [delta_calculator, epsilon_calculator]
    return MarketMakingStrategy(
        dispatcher,
        side=SideTypeEnum.BID,
        instrument=InstrumentTypeEnum.BTC_PLN,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        calculators=calculators,
        database=database,
    )
