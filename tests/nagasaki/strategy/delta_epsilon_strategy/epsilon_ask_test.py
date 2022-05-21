from decimal import Decimal
from unittest import mock

from nagasaki.clients.bitclude.dto import Offer

from nagasaki.enums.common import SideTypeEnum
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList
from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy_ask import (
    DeltaEpsilonStrategyAsk,
    Tolerance,
)


def test_ask_bidding_over_epsilon_without_own_orders(initialized_state: State):
    state = initialized_state
    state.bitclude.active_offers = []

    bitclude_client = mock.Mock()

    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client)

    top_ask_offer = min(state.bitclude.orderbook_rest.asks, key=lambda x: x.price)
    top_ask = top_ask_offer.price
    epsilon = strategy.epsilon

    strategy.get_actions()

    bitclude_client.create_order.assert_called_once()
    result_order = bitclude_client.create_order.call_args[0][0]

    price_to_ask = top_ask - epsilon
    assert result_order.side == SideTypeEnum.ASK
    assert result_order.price == price_to_ask
    assert result_order.amount == Decimal("1")


def test_own_order_outside_tolerance_should_cancel_and_create(initialized_state: State):

    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = 200_000
    own_ask_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    bitclude_client.cancel_and_wait.assert_called_once()
    result_cancel_order = bitclude_client.cancel_and_wait.call_args[0][0]
    assert result_cancel_order.side == SideTypeEnum.ASK
    assert result_cancel_order.price == state.bitclude.active_offers[0].price
    assert result_cancel_order.amount == Decimal("1")

    bitclude_client.create_order.assert_called_once()
    result_create_order = bitclude_client.create_order.call_args[0][0]
    assert result_create_order.side == SideTypeEnum.ASK
    assert result_create_order.price == Decimal("169_999.99")
    assert result_create_order.amount == Decimal("1")


def test_own_order_inside_tolerance_should_not_cancel_and_create(
    initialized_state: State,
):
    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = "169_999.99"
    own_ask_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    bitclude_client.cancel_and_wait.assert_not_called()
    bitclude_client.create_order.assert_not_called()


def make_offer(price, amount):
    return Offer(
        price=Decimal(price),
        amount=Decimal(amount),
        offertype="ask",
        currency1="btc",
        currency2="pln",
        id_user_open="1337",
        nr="421",
        time_open="2020-01-01T00:00:00Z",
    )


def make_orderbook(price, amount):
    return OrderbookRest(
        asks=OrderbookRestList(
            [OrderbookRestItem(price=Decimal(price), amount=Decimal(amount))]
        )
    )
