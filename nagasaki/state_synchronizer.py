from dependency_injector.wiring import Provide, inject

from nagasaki.clients import YahooFinanceClient
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.containers import Application
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState


class StateSynchronizer:
    def synchronize_state(self):
        logger.info("Synchronizing state")
        synchronize_bitclude_state()
        synchronize_deribit_state()


@inject
def synchronize_bitclude_state(
    bitclude_state: BitcludeState = Provide[Application.states.bitclude_state],
    bitclude_client: BitcludeClient = Provide[Application.clients.bitclude_client],
):
    runtime_config = RuntimeConfig()
    bitclude_state.account_info = bitclude_client.fetch_account_info()
    bitclude_state.active_offers = bitclude_client.fetch_active_offers()
    bitclude_state.orderbooks[
        runtime_config.market_making_instrument.market_1
    ] = bitclude_client.fetch_orderbook(
        runtime_config.market_making_instrument.market_1
    ).to_orderbook_rest()


@inject
def synchronize_deribit_state(
    deribit_state: DeribitState = Provide[Application.states.deribit_state],
    deribit_client: DeribitClient = Provide[Application.clients.deribit_client],
):
    runtime_config = RuntimeConfig()
    deribit_state.account_summary = deribit_client.fetch_account_summary()
    deribit_state.mark_price[
        runtime_config.market_making_instrument.market_1
    ] = deribit_client.fetch_index_price_in_usd(runtime_config.market_making_instrument)


@inject
def synchronize_yahoo_finance_state(
    yahoo_finance_state: YahooFinanceState = Provide[
        Application.states.yahoo_finance_state
    ],
    yahoo_finance_client: YahooFinanceClient = Provide[
        Application.clients.yahoo_finance_client
    ],
):
    yahoo_finance_state.usd_pln = yahoo_finance_client.fetch_usd_pln_quote()
