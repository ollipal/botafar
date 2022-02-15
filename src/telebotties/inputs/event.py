class Event:
    def __init__(self, name, is_active, sender, origin, time):
        self._name = name
        self._is_active = is_active
        self._sender = sender
        self._origin = origin
        self._time = time

    @property
    def name(self):
        return self._name

    @property
    def is_active(self):
        return self._is_active

    @property
    def sender(self):
        return self._sender

    @property
    def origin(self):
        return self._origin

    @property
    def time(self):
        return self._time

    def __repr__(self):
        return (
            f"Event(name='{self.name}', is_active={self.is_active}, sender='"
            f"{self.sender}', origin='{self.origin}', time={self.time})"
        )
