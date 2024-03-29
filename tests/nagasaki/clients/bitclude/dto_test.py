from decimal import Decimal

import pytest

from nagasaki.clients.bitclude.dto import CancelRequestDTO, CreateRequestDTO
from nagasaki.clients.exchange_client import (
    bitclude_params_parser,
    deribit_params_parser,
)
from nagasaki.enums.common import InstrumentTypeEnum, Side, SideTypeEnum, Symbol, Type
from nagasaki.models.bitclude import Order


@pytest.fixture(name="order_maker")
def fixture_order_maker():
    return Order(
        order_id=2137,
        price=Decimal("420"),
        amount=Decimal("69"),
        instrument=InstrumentTypeEnum.BTC_PLN,
        side=SideTypeEnum.ASK,
        hidden=True,
        symbol=Symbol("BTC/PLN"),
        post_only=True,
        type=Type.LIMIT,
    )


def test_create_request_dto_from_order_maker(order_maker):
    dto = CreateRequestDTO.from_order(order_maker)

    expected_dto = CreateRequestDTO(
        price=Decimal("420"),
        symbol=Symbol("BTC/PLN"),
        type=Type.LIMIT,
        side=Side.SELL,
        amount=Decimal("69"),
        params={"hidden": True, "post_only": True},
    )

    assert dto == expected_dto


def test_create_request_dto_to_method_params():
    dto = CreateRequestDTO(
        price=Decimal("420"),
        symbol=Symbol("BTC/PLN"),
        type=Type.LIMIT,
        side=Side.SELL,
        amount=Decimal("69"),
        params={"hidden": True, "post_only": True},
    )

    method_params = dto.to_kwargs(bitclude_params_parser)

    expected_method_params = {
        "price": "420",
        "amount": "69.0",
        "type": "limit",
        "side": "sell",
        "symbol": "BTC/PLN",
        "params": {"hidden": "1", "post_only": "1"},
    }

    assert method_params == expected_method_params


def test_cancel_request_dto_from_order_maker(order_maker):
    dto = CancelRequestDTO.from_order(order_maker)

    expected_dto = CancelRequestDTO(order_id="2137", side=Side.SELL)

    assert dto == expected_dto


def test_create_request_dto_to_method_params_deribit():
    dto = CreateRequestDTO(
        price=Decimal("420"),
        symbol=Symbol("BTC/PLN"),
        type=Type.LIMIT,
        side=Side.SELL,
        amount=Decimal("69"),
        params={"hidden": True, "post_only": True},
    )

    method_params = dto.to_kwargs(deribit_params_parser)

    expected_method_params = {
        "price": "420",
        "amount": "69.0",
        "type": "limit",
        "side": "sell",
        "symbol": "BTC/PLN",
        "params": {"hidden": True, "post_only": True},
    }

    assert method_params == expected_method_params
