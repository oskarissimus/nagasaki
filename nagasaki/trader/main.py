import os
from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from pytz_deprecation_shim import PytzUsageWarning

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.bitclude_websocket_client import BitcludeWebsocketClient
from nagasaki.clients.coinbase_client import CoinbaseClient
from nagasaki.clients.cryptocompare_client import CryptocompareClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.state_synchronizer import StateSynchronizer
from nagasaki.strategy import DeltaEpsilonStrategyAsk, DeltaEpsilonStrategyBid
from nagasaki.strategy.delta_epsilon_strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy.hedging_strategy import HedgingStrategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.trader.trader_app import TraderApp
from nagasaki.database.database import Base, engine
from nagasaki.settings import Settings

if __name__ == "__main__":
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")

    Base.metadata.create_all(bind=engine)

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

    coinbase_client = CoinbaseClient()
    state = State()

    usd_pln_quoting_client = YahooFinanceClient(settings.yahoo_finance_api_key)

    state_initializer = StateInitializer(
        bitclude_client,
        deribit_client,
        coinbase_client,
        usd_pln_quoting_client,
        state,
    )

    state_synchronizer = StateSynchronizer(state, bitclude_client, deribit_client)

    dispatcher = StrategyOrderDispatcher(client=bitclude_client, state=state)
    des_ask = DeltaEpsilonStrategyAsk(state=state, dispatcher=dispatcher)
    des_bid = DeltaEpsilonStrategyBid(state=state, dispatcher=dispatcher)
    hedging_strategy = HedgingStrategy(state=state, client=deribit_client)
    strategies = [des_ask, des_bid, hedging_strategy]

    strategy_executor = StrategyExecutor(
        strategies=strategies,
        event_manager=event_manager,
        state=state,
    )

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 2})

    cryptocompare_client = CryptocompareClient()

    app = TraderApp(
        bitclude_client=bitclude_client,
        bitclude_websocket_client=bitclude_websocket_client,
        deribit_client=deribit_client,
        state=state,
        event_manager=event_manager,
        scheduler=scheduler,
        cryptocompare_client=cryptocompare_client,
        strategy_executor=strategy_executor,
        state_initializer=state_initializer,
        coinbase_client=coinbase_client,
        usd_pln_quoting_client=usd_pln_quoting_client,
        state_synchronizer=state_synchronizer,
    )

    app.run()
