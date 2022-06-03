from decimal import Decimal
from unittest import mock

from nagasaki.state import State
from nagasaki.strategy import DeltaEpsilonStrategyBid
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator

from .utils import (
    make_orderbook_with_bid,
    make_order_maker_bid,
)


def test_bid_bidding_over_epsilon(initialized_state: State, dispatcher):
    btc_mark_usd = 50_000
    top_bid_price = 170_000
    top_bid_amount = 1

    expected_price = "170_000.01"
    expected_amount = 1

    epsilon = Decimal("0.01")

    state = initialized_state
    state.bitclude.active_offers = []
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info.balances["PLN"].active = Decimal("170_000.01")
    state.bitclude.orderbook_rest = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )

    strategy = DeltaEpsilonStrategyBid(state, dispatcher, epsilon)
    strategy.delta_calculator = DeltaCalculator(Decimal("0.009"), Decimal("0.002"))

    with mock.patch(
        "nagasaki.strategy.market_making_strategy" ".write_order_maker_to_db"
    ):
        strategy.execute()

    expected_create_order = make_order_maker_bid(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
