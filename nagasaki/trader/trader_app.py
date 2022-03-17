from decimal import Decimal

from apscheduler.schedulers.background import BackgroundScheduler
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.coinbase_client import CoinbaseClient
from nagasaki.clients.cryptocompare_client import CryptocompareClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.state_synchronizer import StateSynchronizer
from nagasaki.strategy import Strategy
from nagasaki.strategy_executor import StrategyExecutor


# pylint: disable=too-many-instance-attributes
class TraderApp:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        bitclude_websocket_client: BitcludeWebsocketClient,
        deribit_client: DeribitClient,
        strategy: Strategy,
        state: State,
        event_manager: EventManager,
        scheduler: BackgroundScheduler,
        cryptocompare_client: CryptocompareClient,
        strategy_executor: StrategyExecutor,
        state_initializer: StateInitializer,
        coinbase_client: CoinbaseClient,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
        state_synchronizer: StateSynchronizer,
    ):
        self.bitclude_client = bitclude_client
        self.bitclude_websocket_client = bitclude_websocket_client
        self.deribit_client = deribit_client
        self.strategy = strategy
        self.state = state
        self.event_manager = event_manager
        self.scheduler = scheduler
        self.cryptocompare_client = cryptocompare_client
        self.strategy_executor = strategy_executor
        self.state_initializer = state_initializer
        self.coinbase_client = coinbase_client
        self.usd_pln_quoting_client = usd_pln_quoting_client
        self.state_synchronizer = state_synchronizer

    def attach_state_synchronizer_handlers_to_events(self):
        self.event_manager.subscribe(
            "synchronize_bitclude_state", self.state_synchronizer.synchronize_state
        )

    def attach_strategy_handlers_to_events(self):
        logger.info("attach_strategy_handlers_to_events")
        self.event_manager.subscribe(
            "orderbook_changed", self.strategy_executor.on_orderbook_changed
        )
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

    def attach_jobs_to_scheduler(self):
        # self.scheduler.add_job(tick, "interval", seconds=3)
        self.scheduler.add_job(
            self.get_btc_mark_usd_from_deribit_and_write_to_state,
            "interval",
            seconds=10,
        )
        self.scheduler.add_job(
            self.fetch_usd_pln_and_write_to_state,
            "interval",
            minutes=20,
        )
        # TODO post event orderbook_changed

    def get_btc_mark_usd_from_deribit_and_write_to_state(self):
        self.state.btc_mark_usd = self.deribit_client.fetch_index_price_btc_usd()
        # logger.info(f"{self.state.btc_mark_usd=}")

    def fetch_usd_pln_and_write_to_state(self):
        usd_pln = self.usd_pln_quoting_client.fetch_usd_pln_quote()
        self.state.usd_pln = usd_pln
        logger.info(f"USD_PLN{self.state.usd_pln:.2f}")

    def get_usd_mark_pln_from_coinbase_and_write_to_state(self):
        self.state.usd_pln = Decimal(1) / (
            self.coinbase_client.fetch_pln_mark_price_usd()
        )

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
        self.bitclude_websocket_client.ws.run_forever()
