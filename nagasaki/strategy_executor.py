from typing import List

from dependency_injector.wiring import Provide, inject

from nagasaki.containers import Application
from nagasaki.logger import logger
from nagasaki.strategy.abstract_strategy import AbstractStrategy


@inject
def execute_all_strategies(
    strategies: List[AbstractStrategy] = Provide[
        Application.strategies.strategies_provider
    ],
):
    logger.debug("strategy execution requested")
    for strategy in strategies:
        strategy.execute()
