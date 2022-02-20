import json

from ..constants import INPUT_EVENT


class Event:
    def __init__(self, name, sender, origin, key):
        self._name = name
        self._sender = sender
        self._origin = origin
        # Initial values
        self._updated = False
        # Internal values
        self._key = key
        self._type = INPUT_EVENT

    def _update(self, is_active, time):
        self._updated = True
        self._is_active = is_active
        self._time = time

    def _change_name(self, name):
        """Some inputs change the name"""
        assert self._updated
        self._name = name

    @property
    def name(self):
        assert self._updated
        return self._name

    @property
    def is_active(self):
        assert self._updated
        return self._is_active

    @property
    def sender(self):
        assert self._updated
        return self._sender

    @property
    def origin(self):
        assert self._updated
        return self._origin

    @property
    def time(self):
        assert self._updated
        return self._time

    @property
    def _callback_key(self):
        return (self._key, self.sender, self.origin)

    def _to_json(self):
        assert self._updated
        return json.dumps(
            {
                "key": self._key,
                "sender": self.sender,
                "origin": self.origin,
                "name": self.name,
                "type": self._type,
            }
        )

    def __repr__(self):
        return (
            f"Event(name='{self.name}', is_active={self.is_active}, sender='"
            f"{self.sender}', origin='{self.origin}', time={self.time})"
        )
