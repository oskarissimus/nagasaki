from collections import defaultdict


class EventManager:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, fn):
        self.subscribers[event_type].append(fn)

    def post_event(self, event_type: str, *args, **kwargs):
        for fn in self.subscribers[event_type]:
            fn(*args, **kwargs)
