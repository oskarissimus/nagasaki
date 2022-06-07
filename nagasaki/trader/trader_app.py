import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.state_synchronizer import StateSynchronizer
from nagasaki.strategy_executor import StrategyExecutor


# pylint: disable=too-many-instance-attributes
class TraderApp:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        bitclude_websocket_client: BitcludeWebsocketClient,
        deribit_client: DeribitClient,
        state: State,
        event_manager: EventManager,
        scheduler: BackgroundScheduler,
        strategy_executor: StrategyExecutor,
        state_initializer: StateInitializer,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
        state_synchronizer: StateSynchronizer,
    ):
        self.bitclude_client = bitclude_client
        self.bitclude_websocket_client = bitclude_websocket_client
        self.deribit_client = deribit_client
        self.state = state
        self.event_manager = event_manager
        self.scheduler = scheduler
        self.strategy_executor = strategy_executor
        self.state_initializer = state_initializer
        self.usd_pln_quoting_client = usd_pln_quoting_client
        self.state_synchronizer = state_synchronizer

    def attach_state_synchronizer_handlers_to_events(self):
        self.event_manager.subscribe(
            "synchronize_bitclude_state", self.state_synchronizer.synchronize_state
        )

    def attach_strategy_handlers_to_events(self):
        logger.info("attach_strategy_handlers_to_events")
        self.event_manager.subscribe(
            "strategy_execution_requested",
            self.strategy_executor.on_strategy_execution_requested,
        )

    def attach_bitclude_handlers_to_events(self):
        self.event_manager.subscribe(
            "actions_execution_on_bitclude_requested",
            self.bitclude_client.execute_actions_list,
        )

    def attach_state_handlers_to_events(self):
        self.event_manager.subscribe(
            "created_order",
            self.state.set_own_order,
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

        self.state.deribit.mark_price[
            runtime_config.market_making_instrument.market_1
        ] = self.deribit_client.fetch_index_price_in_usd(
            runtime_config.market_making_instrument
        )
        # logger.info(f"{self.state.btc_mark_usd=}")

    def get_eth_mark_usd_from_deribit_and_write_to_state(self):
        self.state.deribit.mark_price[
            "ETH"
        ] = self.deribit_client.fetch_index_price_eth_usd()

    def fetch_usd_pln_and_write_to_state(self):
        usd_pln = self.usd_pln_quoting_client.fetch_usd_pln_quote()
        self.state.usd_pln = usd_pln
        logger.info(f"USD_PLN{self.state.usd_pln:.2f}")

    def run(self):
        self.state_initializer.initialize_state()
        self.attach_strategy_handlers_to_events()
        self.attach_bitclude_handlers_to_events()
        self.attach_jobs_to_scheduler()
        self.attach_state_synchronizer_handlers_to_events()

        try:
            self.scheduler.start()
            logger.info("scheduler started")
        except (KeyboardInterrupt, SystemExit):
            pass
        uvicorn.run("nagasaki.api.main:app", host="0.0.0.0")
