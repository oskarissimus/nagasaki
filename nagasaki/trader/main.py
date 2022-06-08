from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from pytz_deprecation_shim import PytzUsageWarning

from nagasaki.containers import Clients
from nagasaki.database import database
from nagasaki.enums.common import SideTypeEnum
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.settings import Settings
from nagasaki.state import State
from nagasaki.state_initializer import StateInitializer
from nagasaki.state_synchronizer import StateSynchronizer
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy.hedging_strategy import HedgingStrategy
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.trader.trader_app import TraderApp

if __name__ == "__main__":
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")

    database.Base.metadata.create_all(bind=database.engine)

    settings = Settings()
    clients = Clients()
    clients.config.from_pydantic(settings)

    event_manager = EventManager()

    bitclude_client = clients.bitclude_client()
    deribit_client = clients.deribit_client()
    usd_pln_quoting_client = clients.yahoo_finance_client()

    state = State()
    state_initializer = StateInitializer(
        bitclude_client,
        deribit_client,
        usd_pln_quoting_client,
        state,
    )

    state_synchronizer = StateSynchronizer(state, bitclude_client, deribit_client)

    runtime_config = RuntimeConfig()

    dispatcher = StrategyOrderDispatcher(client=bitclude_client, state=state)
    delta_calculator = DeltaCalculator()
    calculators = [delta_calculator]
    delta_strategy_ask = MarketMakingStrategy(
        state=state,
        dispatcher=dispatcher,
        side=SideTypeEnum.ASK,
        instrument=runtime_config.market_making_instrument,
        calculators=calculators,
    )
    delta_strategy_bid = MarketMakingStrategy(
        state=state,
        dispatcher=dispatcher,
        side=SideTypeEnum.BID,
        instrument=runtime_config.market_making_instrument,
        calculators=calculators,
    )

    hedging_strategy = HedgingStrategy(
        state=state, client=deribit_client, instrument=runtime_config.hedging_instrument
    )
    strategies = [delta_strategy_ask, delta_strategy_bid, hedging_strategy]

    strategy_executor = StrategyExecutor(
        strategies=strategies,
        event_manager=event_manager,
        state=state,
    )

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 2})

    app = TraderApp(
        bitclude_client=bitclude_client,
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
