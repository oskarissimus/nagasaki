from decimal import Decimal

from nagasaki.state import State
from nagasaki.strategy import DeltaEpsilonStrategyBid

from tests.nagasaki.strategy.delta_epsilon_strategy.utils import (
    make_order_maker_bid,
    make_account_info_with_delta_0_002,
    make_orderbook_with_bid,
)


def test_ask_bidding_over_delta(initialized_state: State, dispatcher):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 - delta)
    """
    btc_mark_usd = 50_000
    expected_price = 199_600
    expected_amount = 1

    top_bid_price = 190_000
    top_bid_amount = 1

    state = initialized_state
    state.bitclude.orderbook_rest = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_002()

    strategy = DeltaEpsilonStrategyBid(state, dispatcher)

    strategy.get_actions()

    expected_create_order = make_order_maker_bid(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
