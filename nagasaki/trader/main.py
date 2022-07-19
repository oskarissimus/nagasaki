from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from dependency_injector.wiring import Provide, inject
from pytz_deprecation_shim import PytzUsageWarning

import nagasaki
from nagasaki.clients import YahooFinanceClient
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.containers import Application
from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState
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
    state: State = Provide[Application.states.state_provider],
    bitclude_state: BitcludeState = Provide[Application.states.bitclude_state_provider],
    deribit_state: DeribitState = Provide[Application.states.deribit_state_provider],
    yahoo_finance_state: YahooFinanceState = Provide[
        Application.states.yahoo_finance_state_provider
    ],
):
    filterwarnings("ignore", category=PytzUsageWarning)
    logger.info("start")

    event_manager = EventManager()

    usd_pln_quoting_client = yahoo_finance_client

    scheduler = BackgroundScheduler(job_defaults={"max_instances": 1})

    app = TraderApp(
        bitclude_client=bitclude_client,
        deribit_client=deribit_client,
        state=state,
        bitclude_state=bitclude_state,
        deribit_state=deribit_state,
        yahoo_finance_state=yahoo_finance_state,
        event_manager=event_manager,
        scheduler=scheduler,
        usd_pln_quoting_client=usd_pln_quoting_client,
    )

    app.run()


if __name__ == "__main__":
    application = Application()
    application.wire(modules=[__name__], packages=[nagasaki])
    main()
