import os
from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from pytz_deprecation_shim import PytzUsageWarning

from nagasaki.clients.bitclude.client import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.coinbase_client import CoinbaseClient
from nagasaki.clients.cryptocompare_client import CryptocompareClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.strategy import BitcludeEpsilonStrategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.trader.trader_app import TraderApp


if __name__ == "__main__":
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")
    bitclude_client_url_base: str = os.getenv("BITCLUDE_URL_BASE")
    bitclude_client_id: str = os.getenv("BITCLUDE_ID")
    bitclude_client_key: str = os.getenv("BITCLUDE_KEY")

    event_manager = EventManager()
    bitclude_websocket_client = BitcludeWebsocketClient(event_manager)
    bitclude_client = BitcludeClient(
        bitclude_client_url_base,
        bitclude_client_id,
        bitclude_client_key,
        event_manager=event_manager,
    )
    deribit_client_url_base: str = os.getenv("DERIBIT_URL_BASE")
    deribit_client_id: str = os.getenv("DERIBIT_CLIENT_ID")
    deribit_client_secret: str = os.getenv("DERIBIT_CLIENT_SECRET")
    deribit_client = DeribitClient(
        deribit_client_url_base, deribit_client_id, deribit_client_secret
    )

    coinbase_client = CoinbaseClient()
    state = State()

    state_initializer = StateInitializer(
        bitclude_client,
        deribit_client,
        coinbase_client,
        state,
    )

    strategy = BitcludeEpsilonStrategy(state=state)
    strategy_executor = StrategyExecutor(
        strategy=strategy,
        event_manager=event_manager,
        state=state,
    )

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 2})

    cryptocompare_client = CryptocompareClient()

    state_initializer = StateInitializer(
        bitclude_client,
        deribit_client,
        coinbase_client,
        state,
    )

    app = TraderApp(
        bitclude_client=bitclude_client,
        bitclude_websocket_client=bitclude_websocket_client,
        deribit_client=deribit_client,
        strategy=strategy,
        state=state,
        event_manager=event_manager,
        scheduler=scheduler,
        cryptocompare_client=cryptocompare_client,
        strategy_executor=strategy_executor,
        state_initializer=state_initializer,
        coinbase_client=coinbase_client,
    )

    app.run()
