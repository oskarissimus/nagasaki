from decimal import Decimal

from nagasaki.state import State
from nagasaki.strategy import DeltaEpsilonStrategyAsk

from tests.nagasaki.strategy.delta_epsilon_strategy.utils import (
    make_orderbook_with_ask,
    make_order_maker_ask,
)


def test_ask_bidding_over_epsilon(initialized_state: State, dispatcher):
    top_ask_price = 170_000
    top_ask_amount = 1

    expected_price = "169_999.99"
    expected_amount = 1

    epsilon = Decimal("0.01")

    state = initialized_state
    state.bitclude.orderbook_rest = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )

    strategy = DeltaEpsilonStrategyAsk(state, dispatcher, epsilon)

    strategy.get_actions()

    expected_create_order = make_order_maker_ask(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
