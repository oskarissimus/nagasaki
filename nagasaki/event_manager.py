class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: str, fn):
        if not event_type in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(fn)

    def post_event(self, event_type: str, *args, **kwargs):
        if not event_type in self.subscribers:
            return
        for fn in self.subscribers[event_type]:
            fn(*args, **kwargs)
