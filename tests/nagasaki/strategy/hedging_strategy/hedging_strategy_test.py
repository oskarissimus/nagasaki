from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Balance, Offer
from nagasaki.clients.deribit_client import AccountSummary
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList
from nagasaki.state import BitcludeState, DeribitState, State
from nagasaki.strategy import HedgingStrategy
from nagasaki.strategy_executor import StrategyExecutor


@pytest.fixture(name="event_manager")
def fixture_event_manager():
    return mock.Mock()


@pytest.fixture(name="state")
def fixture_state():
    btc_price_deribit = 40_000
    usd_pln = 4

    active_bitclude_plns = 100_000
    active_bitclude_btcs = 0.5
    inactive_bitclude_btcs = 0.5

    delta_total_deribit = 0.5
    margin_balance_deribit = 0.5

    state = State()
    state.deribit = DeribitState()
    state.deribit.btc_mark_usd = Decimal(btc_price_deribit)
    state.usd_pln = Decimal(usd_pln)
    state.bitclude = BitcludeState()
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(
                active=Decimal(active_btcs), inactive=Decimal(inactive_bitclude_btcs)
            ),
        }
    )
    state.deribit.account_summary = AccountSummary(
        equity=0, delta_total=delta_total_deribit, margin_balance=margin_balance_deribit
    )
    state.bitclude.active_offers = []
    return state


def test_should_short_2_btcs(event_manager, state: State):
    strategy = HedgingStrategy(state)

    actions = strategy.get_actions()

    btcs_to_short = (
        state.bitclude.account_info.balances["BTC"].active
        + state.bitclude.account_info.balances["BTC"].inactive
        + state.deribit.account_summary.delta_total
        + state.deribit.account_summary.margin_balance
    )

    assert len(actions) == 1
    assert actions[0].action_type == ActionTypeEnum.CREATE
    assert actions[0].client == "deribit"
    assert actions[0].order.type == "sell"
    assert actions[0].order.amount_in_usd == btcs_to_short * state.deribit.btc_mark_usd
