from dependency_injector.wiring import Provide, inject

from nagasaki.containers import Application
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import BitcludeState, DeribitState
from nagasaki.state_synchronizer import (
    synchronize_bitclude_state,
    synchronize_deribit_state,
    synchronize_yahoo_finance_state,
)


class StateInitializer:
    def initialize_state(self):
        logger.info("initialize_state")

        synchronize_bitclude_state()
        synchronize_deribit_state()
        synchronize_yahoo_finance_state()
        _log_state()


@inject
def _log_state(
    bitclude_state: BitcludeState = Provide[Application.states.bitclude_state_provider],
    deribit_state: DeribitState = Provide[Application.states.deribit_state_provider],
):
    runtime_config = RuntimeConfig()

    for orderbook in bitclude_state.orderbooks.values():
        logger.info(orderbook)

    logger.info(
        deribit_state.mark_price[runtime_config.market_making_instrument.market_1]
    )
    logger.info("initialized")
