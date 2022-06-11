from datetime import datetime, timedelta
from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.base_client import OrderTaker
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum


@pytest.fixture(name="client")
def fixture_client():
    client = DeribitClient("client-id", "client-secret", "client-url")
    client.token = "fake-token"
    client.token_expiration = datetime.now() + timedelta(minutes=5)
    return client


def test_should_create_params():
    amount = Decimal("20")
    instrument = InstrumentTypeEnum.ETH_PERPETUAL

    params = DeribitClient.create_order_request_params(amount, instrument)

    expected_params = (
        ("amount", 20.0),
        ("instrument_name", "ETH-PERPETUAL"),
        ("time_in_force", "good_til_cancelled"),
        ("type", "market"),
    )

    assert params == expected_params


def test_should_send_sell_btc_perpetual_request(client):
    order = OrderTaker(
        side=SideTypeEnum.ASK,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        amount=Decimal("21.37"),
    )

    with mock.patch("nagasaki.clients.deribit_client.requests") as requests_mock:
        client.create_order(order)

    expected_params = (
        ("amount", 20.0),
        ("instrument_name", "BTC-PERPETUAL"),
        ("time_in_force", "good_til_cancelled"),
        ("type", "market"),
    )
    request_params = requests_mock.get.call_args[1]["params"]
    assert request_params == expected_params

    request_url = requests_mock.get.call_args[0][0]
    assert request_url == "client-url/private/sell"


def test_should_send_buy_eth_perpetual_request(client):
    order = OrderTaker(
        side=SideTypeEnum.BID,
        instrument=InstrumentTypeEnum.ETH_PERPETUAL,
        amount=Decimal("21.37"),
    )

    with mock.patch("nagasaki.clients.deribit_client.requests") as requests_mock:
        client.create_order(order)

    expected_params = (
        ("amount", 20.0),
        ("instrument_name", "ETH-PERPETUAL"),
        ("time_in_force", "good_til_cancelled"),
        ("type", "market"),
    )
    request_params = requests_mock.get.call_args[1]["params"]
    assert request_params == expected_params

    request_url = requests_mock.get.call_args[0][0]
    assert request_url == "client-url/private/buy"
