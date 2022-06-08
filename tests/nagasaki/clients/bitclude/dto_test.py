from decimal import Decimal

import pytest

from nagasaki.clients.base_client import OrderMaker
from nagasaki.clients.bitclude.dto import CancelRequestDTO, CreateRequestDTO
from nagasaki.enums.common import (
    ActionEnum,
    InstrumentTypeEnum,
    MarketEnum,
    SideTypeEnum,
)


@pytest.fixture(name="order_maker")
def fixture_order_maker():
    return OrderMaker(
        order_id=2137,
        price=Decimal("420"),
        amount=Decimal("69"),
        instrument=InstrumentTypeEnum.BTC_PLN,
        side=SideTypeEnum.ASK,
    )


def test_create_request_dto_from_order_maker(order_maker):
    dto = CreateRequestDTO.from_order_maker(order_maker)

    expected_dto = CreateRequestDTO(
        action=ActionEnum.SELL,
        market1=MarketEnum.BTC,
        market2=MarketEnum.PLN,
        amount=Decimal("69"),
        rate=Decimal("420"),
    )

    assert dto == expected_dto


def test_cancel_request_dto_from_order_maker(order_maker):
    dto = CancelRequestDTO.from_order_maker(order_maker)

    expected_dto = CancelRequestDTO(order_id="2137", type=SideTypeEnum.ASK)

    assert dto == expected_dto
