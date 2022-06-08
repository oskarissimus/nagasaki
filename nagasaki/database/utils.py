from nagasaki.clients.base_client import OrderMaker, OrderTaker
from nagasaki.database.database import SessionLocal
from nagasaki.database.models import OrderMakerDB, OrderTakerDB


def write_order_maker_to_db(order: OrderMaker):
    with SessionLocal() as session:
        session.add(OrderMakerDB.from_order_maker(order))
        session.commit()


def write_order_taker_to_db(order: OrderTaker):
    with SessionLocal() as session:
        session.add(OrderTakerDB.from_order_taker(order))
        session.commit()
