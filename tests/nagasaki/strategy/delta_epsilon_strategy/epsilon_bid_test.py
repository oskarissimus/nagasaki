from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import MarketEnum

from .utils import make_order_maker_bid, make_orderbook_with_bid


def test_bid_bidding_over_epsilon(
    dispatcher, strategy_bid, epsilon_calculator, bitclude_state, deribit_state
):
    btc_mark_usd = 50_000
    top_bid_price = 170_000
    top_bid_amount = 1

    expected_price = "170_000.01"
    expected_amount = 1

    epsilon = Decimal("0.01")

    bitclude_state.active_offers = []
    deribit_state.mark_price["BTC"] = Decimal(btc_mark_usd)
    bitclude_state.account_info.balances["PLN"].active = Decimal("170_000.01")
    bitclude_state.orderbooks[MarketEnum.BTC] = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )
    epsilon_calculator.epsilon = epsilon

    with mock.patch("nagasaki.strategy.market_making_strategy.write_order_maker_to_db"):
        strategy_bid.execute()

    expected_create_order = make_order_maker_bid(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
