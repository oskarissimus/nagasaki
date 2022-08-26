import datetime

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from dependency_injector.wiring import Provide

from nagasaki.clients import ExchangeClient
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.containers import Application
from nagasaki.database import Database
from nagasaki.database.models import MyTrades, TradeDB
from nagasaki.enums.common import Symbol
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState
from nagasaki.state_synchronizer import (
    initialize_states,
    synchronize_bitclude_state,
    synchronize_deribit_state,
    synchronize_yahoo_finance_state,
)
from nagasaki.strategy_executor import execute_all_strategies


# pylint: disable=too-many-instance-attributes
class TraderApp:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        bitclude_client: ExchangeClient,
        deribit_client: ExchangeClient,
        state: State,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        event_manager: EventManager,
        scheduler: BackgroundScheduler,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
    ):
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client
        self.state = state
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state
        self.event_manager = event_manager
        self.scheduler = scheduler
        self.usd_pln_quoting_client = usd_pln_quoting_client

    def attach_state_synchronizer_handlers_to_events(self):
        self.event_manager.subscribe("synchronize_state", synchronize_bitclude_state)
        self.event_manager.subscribe("synchronize_state", synchronize_deribit_state)

    def attach_strategy_handlers_to_events(self):
        logger.info("attach_strategy_handlers_to_events")
        self.event_manager.subscribe(
            "strategy_execution_requested",
            execute_all_strategies,
        )

    def synchronize_state_and_execute_strategy(self):
        self.event_manager.post_event("synchronize_state")
        self.save_state_to_database()
        self.event_manager.post_event("strategy_execution_requested")

    def attach_jobs_to_scheduler(self):
        self.scheduler.add_job(
            self.fetch_usd_pln_and_write_to_state,
            "interval",
            minutes=20,
        )
        self.scheduler.add_job(
            self.synchronize_state_and_execute_strategy,
            "interval",
            seconds=10,
        )
        self.scheduler.add_job(
            self.save_my_trades_to_database,
            "interval",
            minutes=5,
            next_run_time=datetime.datetime.now(),
        )
        self.scheduler.add_job(
            self.save_trades_to_database,
            "interval",
            minutes=1,
            next_run_time=datetime.datetime.now(),
        )

    def fetch_usd_pln_and_write_to_state(self):
        synchronize_yahoo_finance_state()
        logger.info(f"USD/PLN: {self.yahoo_finance_state.mark_price['USD/PLN']:.2f}")

    def save_state_to_database(
        self, database: Database = Provide[Application.databases.database_provider]
    ):
        database.write_state_to_db(self.state)

    def save_my_trades_to_database(
        self,
        database: Database = Provide[Application.databases.database_provider],
        client: ExchangeClient = Provide[Application.clients.bitclude_client_provider],
    ):
        symbols = [
            Symbol(strategy.symbol)
            for strategy in database.get_newest_settings().strategies.market_making_strategies
        ]

        for symbol in set(symbols):
            trades = client.fetch_my_trades(symbol)
            trades_db = [MyTrades(**trade.dict(), id=hash(trade)) for trade in trades]
            database.write_my_trades_to_db(trades_db)

    def save_trades_to_database(
        self,
        database: Database = Provide[Application.databases.database_provider],
        client: ExchangeClient = Provide[Application.clients.bitclude_client_provider],
    ):
        symbols = [
            Symbol(strategy.symbol)
            for strategy in database.get_newest_settings().strategies.market_making_strategies
        ]

        for symbol in set(symbols):
            trades = client.fetch_trades(symbol)
            trades_db = [TradeDB.from_trade(trade) for trade in trades]
            database.write_trades_to_db(trades_db)

    def run(self):
        initialize_states()
        self.attach_strategy_handlers_to_events()
        self.attach_jobs_to_scheduler()
        self.attach_state_synchronizer_handlers_to_events()

        try:
            self.scheduler.start()
            logger.info("scheduler started")
        except (KeyboardInterrupt, SystemExit):
            pass
        uvicorn.run("nagasaki.api.main:app", host="0.0.0.0")
