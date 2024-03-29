from unittest import mock
from unittest.mock import call

import pytest

from nagasaki.state import BitcludeState
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher, Tolerance

from .utils import make_offer, make_order_maker_ask


@pytest.fixture(name="dispatcher")
def fixture_dispatcher(client, bitclude_state):
    tolerance = Tolerance(amount=1, price=1)
    return StrategyOrderDispatcher(client, bitclude_state, tolerance)


@pytest.fixture(name="client")
def fixture_client():
    return mock.Mock()


@pytest.fixture(name="bitclude_state")
def fixture_bitclude_state():
    return BitcludeState()


def test_should_create_for_0_own_offers(dispatcher, client):
    desirable_order = make_order_maker_ask(100, 1, True)

    dispatcher.dispatch(desirable_order)

    client.create_order.assert_called_once_with(desirable_order)


def test_should_cancel_and_create_for_1_own_offer_outside_tolerance(
    dispatcher, client, bitclude_state
):
    own_offer = make_offer(price=99, amount=1)
    bitclude_state.active_offers = [own_offer]
    dispatcher.tolerance = Tolerance(price=1, amount=1)

    desirable_order = make_order_maker_ask(100, 1, True)

    dispatcher.dispatch(desirable_order)

    expected_cancel_order = dispatcher.active_offers[0].to_order_maker()
    client.cancel_order.assert_called_once_with(expected_cancel_order)

    client.create_order.assert_called_once_with(desirable_order)


def test_should_not_cancel_nor_create_for_1_own_offer_inside_tolerance(
    dispatcher, client, bitclude_state
):
    own_offer = make_offer(price=99, amount=1)
    bitclude_state.active_offers = [own_offer]
    dispatcher.tolerance = Tolerance(price=2, amount=1)

    desirable_order = make_order_maker_ask(100, 1, True)

    dispatcher.dispatch(desirable_order)

    client.cancel_and_wait.assert_not_called()
    client.create_order.assert_not_called()


@pytest.mark.skip
def should_cancel_all_and_create_for_multiple_offers(
    dispatcher, client, bitclude_state
):
    own_offer_1 = make_offer(price=99, amount=1)
    own_offer_2 = make_offer(price=101, amount=1)
    bitclude_state.active_offers = [own_offer_1, own_offer_2]

    desirable_order = make_order_maker_ask(100, 1, True)

    dispatcher.dispatch(desirable_order)

    assert client.cancel_order.call_count == 2
    expected_cancel_orders = [
        offer.to_order_maker() for offer in bitclude_state.active_offers
    ]
    expected_calls = [call(order) for order in expected_cancel_orders]
    client.cancel_order.assert_has_calls(expected_calls, any_order=True)

    client.create_order.assert_called_once_with(desirable_order)
