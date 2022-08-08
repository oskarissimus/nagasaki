from unittest import mock

from nagasaki.clients import ExchangeClient
from nagasaki.enums.common import InstrumentTypeEnum, Side, SideTypeEnum, Symbol, Type
from nagasaki.models.bitclude import Order


def test_should_create_order_from_order_maker():
    order_maker = Order(
        side=SideTypeEnum.BID,
        amount=1,
        instrument=InstrumentTypeEnum.BTC_PLN,
        price=1000,
        symbol=Symbol.BTC_PLN,
        hidden=True,
        post_only=True,
        type=Type.LIMIT,
    )

    client = ExchangeClient("bitclude", "client_id", "client_key")

    with mock.patch.object(client, "ccxt_connector") as mock_ccxt:
        client.create_order(order_maker)

        mock_ccxt.create_order.assert_called_once_with(
            price="1000",
            symbol=Symbol.BTC_PLN.value,
            side=Side.BUY.lower(),
            amount="1.0",
            type="limit",
            params={"hidden": "1", "post_only": "1"},
        )


def test_should_create_order_from_order_taker():
    order_taker = Order(
        side=SideTypeEnum.ASK,
        amount=100,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
        hidden=False,
        post_only=False,
        type=Type.MARKET,
    )

    client = ExchangeClient(
        "deribit", client_id="client_id", client_secret="client_secret"
    )

    with mock.patch.object(client, "ccxt_connector") as mock_ccxt:
        client.create_order(order_taker)

    mock_ccxt.create_order.assert_called_once_with(
        price=None,
        side=Side.SELL.lower(),
        symbol=Symbol.BTC_USD_BTC.value,
        amount="100.0",
        type="market",
        params={"hidden": False, "post_only": False},
    )
