from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from nagasaki.database.models import Base, OrderMakerDB, OrderTakerDB
from nagasaki.models.bitclude import Order, OrderMaker, OrderTaker


class Database:
    def __init__(self, session_maker: sessionmaker, engine: Engine):
        self.session_maker = session_maker

        Base.metadata.create_all(bind=engine)

    def save_order(self, order: Order):
        if isinstance(order, OrderMaker):
            self.write_order_maker_to_db(order)
        if isinstance(order, OrderTaker):
            self.write_order_taker_to_db(order)

    def write_order_taker_to_db(self, order: OrderTaker):
        with self.session_maker() as session:
            session.add(OrderTakerDB.from_order_taker(order))
            session.commit()

    def write_order_maker_to_db(self, order: OrderMaker):
        with self.session_maker() as session:
            session.add(OrderMakerDB.from_order_maker(order))
            session.commit()
