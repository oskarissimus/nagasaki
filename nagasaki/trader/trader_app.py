import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.state_synchronizer import (
    initialize_states,
    synchronize_bitclude_state,
    synchronize_yahoo_finance_state,
)
from nagasaki.strategy_executor import execute_all_strategies


# pylint: disable=too-many-instance-attributes
class TraderApp:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        deribit_client: DeribitClient,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
        event_manager: EventManager,
        scheduler: BackgroundScheduler,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
    ):
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state
        self.event_manager = event_manager
        self.scheduler = scheduler
        self.usd_pln_quoting_client = usd_pln_quoting_client

    def attach_state_synchronizer_handlers_to_events(self):
        self.event_manager.subscribe(
            "synchronize_bitclude_state", synchronize_bitclude_state
        )

    def attach_strategy_handlers_to_events(self):
        logger.info("attach_strategy_handlers_to_events")
        self.event_manager.subscribe(
            "strategy_execution_requested",
            execute_all_strategies,
        )

    def synchronize_state_and_execute_strategy(self):
        self.event_manager.post_event("synchronize_bitclude_state")
        self.event_manager.post_event("strategy_execution_requested")

    def attach_jobs_to_scheduler(self):
        # self.scheduler.add_job(tick, "interval", seconds=3)
        self.scheduler.add_job(
            self.get_mark_price_in_usd_from_deribit_and_write_to_state,
            "interval",
            seconds=10,
        )
        self.scheduler.add_job(
            self.fetch_usd_pln_and_write_to_state,
            "interval",
            minutes=20,
        )
        # TODO post event orderbook_changed
        self.scheduler.add_job(
            self.synchronize_state_and_execute_strategy,
            "interval",
            seconds=10,
        )

    def get_mark_price_in_usd_from_deribit_and_write_to_state(self):
        runtime_config = RuntimeConfig()

        self.deribit_state.mark_price[
            runtime_config.market_making_instrument.market_1
        ] = self.deribit_client.fetch_index_price_in_usd(
            runtime_config.market_making_instrument
        )
        # logger.info(f"{self.state.btc_mark_usd=}")

    def fetch_usd_pln_and_write_to_state(self):
        synchronize_yahoo_finance_state()
        logger.info(f"USD_PLN{self.yahoo_finance_state.usd_pln:.2f}")

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
