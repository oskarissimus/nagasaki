from unittest import mock

from nagasaki.strategy_executor import StrategyExecutor


def test_should_post_actions_execution_request():
    actions_1 = [mock.Mock(), mock.Mock(), mock.Mock()]
    strategy_1 = mock.Mock()
    strategy_1.get_actions.return_value = actions_1

    actions_2 = [mock.Mock(), mock.Mock()]
    strategy_2 = mock.Mock()
    strategy_2.get_actions.return_value = actions_2

    strategies = [strategy_1, strategy_2]
    event_manager = mock.Mock()
    strategy_executor = StrategyExecutor(strategies, event_manager, mock.Mock())

    strategy_executor.on_strategy_execution_requested()

    expected_actions = actions_1 + actions_2
    result_actions = event_manager.post_event.call_args[0][1]
    assert set(result_actions) == set(expected_actions)
