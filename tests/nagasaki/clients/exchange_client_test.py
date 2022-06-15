from unittest import mock

from nagasaki.clients.base_client import OrderMaker, OrderTaker
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.enums.common import InstrumentTypeEnum, Side, SideTypeEnum, Symbol


def test_should_create_order_from_order_maker():
    order_maker = OrderMaker(
        side=SideTypeEnum.BID,
        amount=1,
        instrument=InstrumentTypeEnum.BTC_PLN,
        price=1000,
        symbol=Symbol.BTC_PLN,
        hidden=True,
    )

    client = BitcludeClient("client_id", "client_key")

    with mock.patch.object(client, "ccxt_connector") as mock_ccxt:
        client.create_order(order_maker)

        mock_ccxt.create_order.assert_called_once_with(
            price="1000",
            symbol=Symbol.BTC_PLN.value,
            side=Side.BUY.lower(),
            amount="1.0",
            type="limit",
            params={"hidden": True, "post_only": True},
        )


def test_should_create_order_from_order_taker():
    order_taker = OrderTaker(
        side=SideTypeEnum.ASK,
        amount=100,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
        hidden=False,
    )

    client = DeribitClient("client_id", "client_secret")

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
