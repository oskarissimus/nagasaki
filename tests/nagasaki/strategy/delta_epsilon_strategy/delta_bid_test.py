from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import MarketEnum
from nagasaki.state import State

from .utils import (
    make_account_info_with_delta_0_009,
    make_order_maker_bid,
    make_orderbook_with_bid,
)


def test_bid_bidding_over_delta(initialized_state: State, dispatcher, strategy_bid):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 - delta)
    """
    btc_mark_usd = 50_000
    expected_price = 198_200
    expected_amount = 1

    top_bid_price = 199_000
    top_bid_amount = 1

    state = initialized_state
    state.bitclude.orderbooks[MarketEnum.BTC] = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )
    state.deribit.mark_price["BTC"] = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_009()

    with mock.patch("nagasaki.strategy.market_making_strategy.write_order_maker_to_db"):
        strategy_bid.execute(state)

    expected_create_order = make_order_maker_bid(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
