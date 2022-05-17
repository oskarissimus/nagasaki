from unittest import mock

import pytest

from nagasaki.event_manager import EventManager


@pytest.fixture(name="event_manager")
def fixture_event_manager():
    return EventManager()


def test_should_notify_one_subscriber(event_manager: EventManager):
    callback_fn = mock.Mock()
    event_manager.subscribe("test-event", callback_fn)

    event_manager.post_event("test-event")

    callback_fn.assert_called_once()


def test_should_notify_multiple_subscribers(event_manager: EventManager):
    callback_fn_1 = mock.Mock()
    callback_fn_2 = mock.Mock()
    event_manager.subscribe("test-event", callback_fn_1)
    event_manager.subscribe("test-event", callback_fn_2)

    event_manager.post_event("test-event")

    callback_fn_1.assert_called_once()
    callback_fn_2.assert_called_once()


def test_should_notify_correct_subscribers(event_manager: EventManager):
    callback_fn_1 = mock.Mock()
    callback_fn_2 = mock.Mock()
    event_manager.subscribe("test-event-1", callback_fn_1)
    event_manager.subscribe("test-event-2", callback_fn_2)

    event_manager.post_event("test-event-1")

    callback_fn_1.assert_called_once()
    callback_fn_2.assert_not_called()


def test_should_notify_with_args(event_manager: EventManager):
    callback_fn = mock.Mock()
    event_manager.subscribe("test-event", callback_fn)

    event_manager.post_event("test-event", 42)

    callback_fn.assert_called_once_with(42)


def test_should_notify_with_kwargs(event_manager: EventManager):
    callback_fn = mock.Mock()
    event_manager.subscribe("test-event", callback_fn)

    event_manager.post_event(event_type="test-event", answer=42)

    callback_fn.assert_called_once_with(answer=42)
