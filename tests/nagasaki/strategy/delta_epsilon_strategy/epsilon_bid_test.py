from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import MarketEnum
from nagasaki.state import State

from .utils import (
    make_orderbook_with_bid,
    make_order_maker_bid,
)


def test_bid_bidding_over_epsilon(
    initialized_state: State, dispatcher, strategy_bid, epsilon_calculator
):
    btc_mark_usd = 50_000
    top_bid_price = 170_000
    top_bid_amount = 1

    expected_price = "170_000.01"
    expected_amount = 1

    epsilon = Decimal("0.01")

    state = initialized_state
    state.bitclude.active_offers = []
    state.deribit.mark_price["BTC"] = Decimal(btc_mark_usd)
    state.bitclude.account_info.balances["PLN"].active = Decimal("170_000.01")
    state.bitclude.orderbooks[MarketEnum.BTC] = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )
    epsilon_calculator.epsilon = epsilon

    with mock.patch("nagasaki.strategy.market_making_strategy.write_order_maker_to_db"):
        strategy_bid.execute()

    expected_create_order = make_order_maker_bid(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
