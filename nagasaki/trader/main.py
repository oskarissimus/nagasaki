from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from dependency_injector.wiring import Provide, inject
from pytz_deprecation_shim import PytzUsageWarning

import nagasaki
from nagasaki.clients import YahooFinanceClient
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.containers import Application
from nagasaki.database import database
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.hedging_strategy import HedgingStrategy
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy
from nagasaki.strategy_executor import StrategyExecutor
from nagasaki.trader.trader_app import TraderApp


@inject
def main(
    bitclude_client: BitcludeClient = Provide[
        Application.clients.bitclude_client_provider
    ],
    deribit_client: DeribitClient = Provide[
        Application.clients.deribit_client_provider
    ],
    yahoo_finance_client: YahooFinanceClient = Provide[
        Application.clients.yahoo_finance_client_provider
    ],
    bitclude_state: BitcludeState = Provide[Application.states.bitclude_state_provider],
    deribit_state: DeribitState = Provide[Application.states.deribit_state_provider],
    yahoo_finance_state: YahooFinanceState = Provide[
        Application.states.yahoo_finance_state_provider
    ],
    market_making_strategy_bid: MarketMakingStrategy = Provide[
        Application.strategies.market_making_strategy_bid
    ],
    market_making_strategy_ask: MarketMakingStrategy = Provide[
        Application.strategies.market_making_strategy_ask
    ],
    hedging_strategy: HedgingStrategy = Provide[
        Application.strategies.hedging_strategy
    ],
):
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")

    database.Base.metadata.create_all(bind=database.engine)

    event_manager = EventManager()

    usd_pln_quoting_client = yahoo_finance_client

    strategies = [
        market_making_strategy_ask,
        market_making_strategy_bid,
        hedging_strategy,
    ]

    strategy_executor = StrategyExecutor(
        strategies=strategies,
        event_manager=event_manager,
    )

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 2})

    app = TraderApp(
        bitclude_client=bitclude_client,
        deribit_client=deribit_client,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        event_manager=event_manager,
        scheduler=scheduler,
        strategy_executor=strategy_executor,
        usd_pln_quoting_client=usd_pln_quoting_client,
    )

    app.run()


if __name__ == "__main__":
    application = Application()
    application.wire(modules=[__name__], packages=[nagasaki])
    main()
