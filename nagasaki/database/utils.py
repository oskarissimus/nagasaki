from typing import List
from nagasaki.clients.base_client import OrderMaker, OrderTaker

from nagasaki.models.bitclude import Action as BitcludeAction
from nagasaki.database.database import SessionLocal
from nagasaki.database.models import Action, OrderMakerDB, OrderTakerDB


def dump_actions_to_db(actions: List[BitcludeAction]):
    actions = [Action.from_action(action) for action in actions]
    with SessionLocal() as session:
        for action in actions:
            session.add(action)
        session.commit()


def write_order_maker_to_db(order: OrderMaker):
    with SessionLocal() as session:
        session.add(OrderMakerDB.from_order_maker(order))
        session.commit()


def write_order_taker_to_db(order: OrderTaker):
    with SessionLocal() as session:
        session.add(OrderTakerDB.from_order_taker(order))
        session.commit()
