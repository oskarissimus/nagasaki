from unittest import mock

from nagasaki.strategy_executor import StrategyExecutor


def test_should_execute_strategies():
    strategy_1 = mock.Mock()
    strategy_2 = mock.Mock()

    strategies = [strategy_1, strategy_2]
    event_manager = mock.Mock()
    strategy_executor = StrategyExecutor(strategies, event_manager)

    strategy_executor.on_strategy_execution_requested()

    strategy_1.execute.assert_called_once()
    strategy_2.execute.assert_called_once()
