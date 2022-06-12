from decimal import Decimal

from nagasaki.enums.common import MarketEnum

from .utils import make_order_maker_ask, make_orderbook_with_ask


def test_ask_bidding_over_epsilon(
    dispatcher, epsilon_calculator, strategy_ask, bitclude_state
):
    top_ask_price = 170_000
    top_ask_amount = 1

    expected_price = "169_999.99"
    expected_amount = 1

    epsilon = Decimal("0.01")

    bitclude_state.orderbooks[MarketEnum.BTC] = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )
    epsilon_calculator.epsilon = epsilon

    result_order = strategy_ask.execute()

    expected_create_order = make_order_maker_ask(expected_price, expected_amount)

    assert result_order == expected_create_order
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
