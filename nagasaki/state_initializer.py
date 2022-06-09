from dependency_injector.wiring import Provide, inject

from nagasaki.containers import Application
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import State
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
def _log_state(state: State = Provide[Application.states.state]):
    runtime_config = RuntimeConfig()

    for orderbook in state.bitclude.orderbooks.values():
        logger.info(orderbook)

    logger.info(
        state.deribit.mark_price[runtime_config.market_making_instrument.market_1]
    )
    logger.info("initialized")
