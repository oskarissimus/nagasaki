from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from nagasaki.clients.bitclude.dto import AccountInfo
from nagasaki.database.models import (
    BalanceDB,
    Base,
    OrderMakerDB,
    OrderTakerDB,
    Settings,
    Snapshot,
)
from nagasaki.models.bitclude import Order, OrderMaker, OrderTaker
from nagasaki.settings.runtime import RuntimeSettings, StrategySettingsList
from nagasaki.state import State


class Database:
    def __init__(self, session_maker: sessionmaker, engine: Engine):
        self.session_maker = session_maker

        Base.metadata.create_all(bind=engine)
        # auto_base = automap_base(metadata=Base.metadata)
        # auto_base.prepare(engine, reflect=True)

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

    def write_account_info_to_db(self, account_info: AccountInfo):
        with self.session_maker() as session:
            for currency, balance in account_info.balances.items():
                if not balance.active == balance.inactive == 0:
                    session.add(
                        BalanceDB(
                            currency=currency,
                            amount_active=balance.active,
                            amount_inactive=balance.inactive,
                        )
                    )
            session.commit()

    def write_state_to_db(self, state: State):
        snapshot = Snapshot(state=state.json())
        with self.session_maker() as session:
            session.add(snapshot)
            session.commit()

    def write_settings_to_db(self, runtime_settings: RuntimeSettings):
        settings = Settings(settings=runtime_settings.json())
        with self.session_maker() as session:
            session.add(settings)
            session.commit()

    def get_newest_settings(self) -> RuntimeSettings:
        with self.session_maker() as session:
            settings_db = session.query(Settings).order_by(Settings.time.desc()).first()
            if settings_db is None:
                return RuntimeSettings(
                    market_making_instrument="ETH_PLN",
                    hedging_instrument="ETH_PERPETUAL",
                    strategies=StrategySettingsList(),
                )
            return RuntimeSettings.parse_raw(settings_db.settings)
