from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Balance
from nagasaki.clients.deribit_client import AccountSummary
from nagasaki.enums.common import InstrumentTypeEnum
from nagasaki.state import BitcludeState, DeribitState, State
from nagasaki.strategy.hedging_strategy import HedgingStrategy
from .utils import make_order_taker_buy


@pytest.fixture(name="state")
def fixture_state():
    btc_price_deribit = 40_000
    usd_pln = 4

    active_bitclude_plns = 100_000
    inactive_bitclude_plns = 0
    active_bitclude_btcs = 0.5
    inactive_bitclude_btcs = 0.5

    # Only delta_total_deribit can be negative
    delta_total_deribit = -3.5
    margin_balance_deribit = 0.5

    state = State()
    state.deribit = DeribitState()
    state.deribit.mark_price["BTC"] = Decimal(btc_price_deribit)
    state.usd_pln = Decimal(usd_pln)
    state.bitclude = BitcludeState()
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(
                active=Decimal(active_bitclude_plns),
                inactive=Decimal(inactive_bitclude_plns),
            ),
            "BTC": Balance(
                active=Decimal(active_bitclude_btcs),
                inactive=Decimal(inactive_bitclude_btcs),
            ),
        }
    )
    state.deribit.account_summary = AccountSummary(
        equity=0, delta_total=delta_total_deribit, margin_balance=margin_balance_deribit
    )
    state.bitclude.active_offers = []
    return state


def test_should_long_2_btcs(state: State, client: mock.Mock):
    btcs_to_long_in_dollars = 80_000

    strategy = HedgingStrategy(state, client, InstrumentTypeEnum.BTC_PERPETUAL)

    with mock.patch("nagasaki.strategy.hedging_strategy.write_order_taker_to_db"):
        strategy.execute()

    expected_create_order = make_order_taker_buy(
        amount=Decimal(btcs_to_long_in_dollars)
    )
    client.create_order.assert_called_once_with(expected_create_order)
