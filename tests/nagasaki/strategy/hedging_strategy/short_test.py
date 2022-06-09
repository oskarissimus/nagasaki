from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Balance
from nagasaki.clients.deribit_client import AccountSummary
from nagasaki.enums.common import InstrumentTypeEnum
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.hedging_strategy import HedgingStrategy

from .utils import make_order_taker_sell


@pytest.fixture(name="bitclude_state")
def fixture_bitclude_state():
    active_bitclude_plns = 100_000
    inactive_bitclude_plns = 0
    active_bitclude_btcs = 0.5
    inactive_bitclude_btcs = 0.5

    bitclude = BitcludeState()
    bitclude.account_info = AccountInfo(
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
    bitclude.active_offers = []

    return bitclude


@pytest.fixture(name="deribit_state")
def fixture_deribit_state():
    btc_price_deribit = 40_000

    delta_total_deribit = 0.5
    margin_balance_deribit = 0.5

    deribit = DeribitState()
    deribit.mark_price["BTC"] = Decimal(btc_price_deribit)
    deribit.account_summary = AccountSummary(
        equity=0, delta_total=delta_total_deribit, margin_balance=margin_balance_deribit
    )

    return deribit


@pytest.fixture(name="yahoo_finance_state")
def fixture_yahoo_finanace_state():
    usd_pln = 4

    yahoo = YahooFinanceState()
    yahoo.usd_pln = Decimal(usd_pln)

    return yahoo


def test_should_short_2_btcs(
    client: mock.Mock, bitclude_state, deribit_state, yahoo_finance_state
):
    btcs_to_short_in_dollars = 80_000

    strategy = HedgingStrategy(
        client,
        InstrumentTypeEnum.BTC_PERPETUAL,
        bitclude_state,
        deribit_state,
        yahoo_finance_state,
    )

    with mock.patch("nagasaki.strategy.hedging_strategy.write_order_taker_to_db"):
        strategy.execute()

    expected_create_order = make_order_taker_sell(
        amount=Decimal(btcs_to_short_in_dollars)
    )
    client.create_order.assert_called_once_with(expected_create_order)
