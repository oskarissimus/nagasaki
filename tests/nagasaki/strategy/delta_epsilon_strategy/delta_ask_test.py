from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import MarketEnum
from nagasaki.state import State

from .utils import (
    make_account_info_with_delta_0_002,
    make_order_maker_ask,
    make_orderbook_with_ask,
)


def test_ask_bidding_over_delta(initialized_state: State, dispatcher, strategy_ask):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    top_ask_price = 170_000
    top_ask_amount = 1

    state = initialized_state
    state.deribit.mark_price["BTC"] = Decimal(btc_mark_usd)
    state.bitclude.orderbooks[MarketEnum.BTC] = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )
    state.bitclude.account_info = make_account_info_with_delta_0_002()

    with mock.patch("nagasaki.strategy.market_making_strategy.write_order_maker_to_db"):
        strategy_ask.execute(state)

    expected_create_order = make_order_maker_ask(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
