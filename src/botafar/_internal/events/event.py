import json

from ..constants import INPUT_EVENT


class Event:
    def __init__(self, name, sender, key):
        self._name = name
        self._sender = sender
        # Initial values
        self._time = None
        self._is_active = None
        # Internal values
        self._key = key
        self._type = INPUT_EVENT

    def _set_time(self, time):
        self._time = time

    def _set_active_method(self, is_active):
        self._is_active = is_active

    def _change_name(self, name):
        """Some controls change the name"""
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def is_active(self):
        assert self._is_active is not None
        return self._is_active()

    @property
    def sender(self):
        return self._sender

    @property
    def time(self):
        assert self._time is not None
        return self._time

    @property
    def _callback_key(self):
        return (self._key, self.sender)

    def _to_json(self):
        return json.dumps(
            {
                "key": self._key,
                "sender": self.sender,
                "name": self.name,
                "type": self._type,
            }
        )

    def __repr__(self):
        return (
            f"Event(name='{self.name}', is_active={self.is_active}, sender='"
            f"{self.sender}', time={self.time})"
        )
