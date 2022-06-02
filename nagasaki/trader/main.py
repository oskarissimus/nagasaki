from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from pytz_deprecation_shim import PytzUsageWarning

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.state_synchronizer import StateSynchronizer

from nagasaki.strategy.delta_epsilon_strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy import DeltaStrategyAsk, DeltaStrategyBid

from nagasaki.strategy.hedging_strategy import HedgingStrategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.trader.trader_app import TraderApp
from nagasaki.database import database
from nagasaki.settings import Settings

if __name__ == "__main__":
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")

    database.init_db()
    database.Base.metadata.create_all(bind=database.engine)

    settings = Settings()

    event_manager = EventManager()
    bitclude_websocket_client = BitcludeWebsocketClient(event_manager)
    bitclude_client = BitcludeClient(
        settings.bitclude_url_base,
        settings.bitclude_id,
        settings.bitclude_key,
        event_manager=event_manager,
    )
    deribit_client = DeribitClient(
        settings.deribit_url_base,
        settings.deribit_client_id,
        settings.deribit_client_secret,
    )

    state = State()

    usd_pln_quoting_client = YahooFinanceClient(settings.yahoo_finance_api_key)

    state_initializer = StateInitializer(
        bitclude_client,
        deribit_client,
        usd_pln_quoting_client,
        state,
    )

    state_synchronizer = StateSynchronizer(state, bitclude_client, deribit_client)

    dispatcher = StrategyOrderDispatcher(client=bitclude_client, state=state)
    des_ask = DeltaStrategyAsk(state=state, dispatcher=dispatcher)
    des_bid = DeltaStrategyBid(state=state, dispatcher=dispatcher)
    hedging_strategy = HedgingStrategy(state=state, client=deribit_client)
    strategies = [des_ask, des_bid, hedging_strategy]

    strategy_executor = StrategyExecutor(
        strategies=strategies,
        event_manager=event_manager,
        state=state,
    )

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 2})

    app = TraderApp(
        bitclude_client=bitclude_client,
        bitclude_websocket_client=bitclude_websocket_client,
        deribit_client=deribit_client,
        state=state,
        event_manager=event_manager,
        scheduler=scheduler,
        strategy_executor=strategy_executor,
        state_initializer=state_initializer,
        usd_pln_quoting_client=usd_pln_quoting_client,
        state_synchronizer=state_synchronizer,
    )

    app.run()
