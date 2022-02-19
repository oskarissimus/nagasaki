from apscheduler.schedulers.background import BackgroundScheduler
from nagasaki.clients.bitclude_client import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.cryptocompare_client import CryptocompareClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.event_manager import EventManager
from nagasaki.state import State
from nagasaki.strategy import Strategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.logger import logger


class TraderApp:
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

    def attach_strategy_handlers_to_events(self):
        logger.info("attach_strategy_handlers_to_events")
        self.event_manager.subscribe(
            "orderbook_changed", self.strategy_executor.on_orderbook_changed
        )
        logger.info("attached")

    def attach_bitclude_handlers_to_events(self):
        self.event_manager.subscribe(
            "actions_execution_on_bitclude_requested",
            self.bitclude_client.execute_actions_list,
        )

    def attach_jobs_to_scheduler(self):
        # self.scheduler.add_job(tick, "interval", seconds=3)
        self.scheduler.add_job(
            self.get_btc_mark_usd_from_deribit_and_write_to_state,
            "interval",
            seconds=10,
        )
        self.scheduler.add_job(
            self.get_usd_mark_pln_from_cryptocompare_and_write_to_state,
            "interval",
            seconds=10,
        )
        # TODO post event orderbook_changed

    def get_btc_mark_usd_from_deribit_and_write_to_state(self):
        self.state.btc_mark_usd = self.deribit_client.fetch_index_price_btc_usd()
        # print(f"{self.state.btc_mark_usd=}")

    def get_usd_mark_pln_from_cryptocompare_and_write_to_state(self):
        cryptocompare_data = self.cryptocompare_client.fetch_histominute_data()
        cryptocompare_usd_mark_price_pln = (
            self.cryptocompare_client.calculate_mean_of_mids_from_last_20_minutes(
                cryptocompare_data
            )
        )
        self.state.usd_pln = cryptocompare_usd_mark_price_pln
        # print(f"{self.state.usd_pln=}")

    def run(self):
        self.attach_strategy_handlers_to_events()
        self.attach_bitclude_handlers_to_events()
        self.attach_jobs_to_scheduler()
        try:
            self.scheduler.start()
            logger.info("scheduler started")
        except (KeyboardInterrupt, SystemExit):
            pass
        self.bitclude_websocket_client.ws.run_forever()
