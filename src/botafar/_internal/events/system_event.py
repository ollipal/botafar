import json

from ..constants import SYSTEM_EVENT


class SystemEvent:
    def __init__(self, name, value, text="", data=None):
        self._type = SYSTEM_EVENT
        self._name = name
        self._value = value
        self._text = text
        self._data = data

    def set_value(self, value):
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

    @property
    def data(self):
        return self._data

    def _to_json(self):
        return json.dumps(
            {
                "type": self._type,
                "name": self.name,
                "value": self.value,
                "text": self.text,
                "data": self.data,
            }
        )

    def __repr__(self):
        return (
            f"SystemEvent(name='{self.name}', value={self.value}, "
            f"text='{self.text}' {'+ data' if self.data else ''})"
        )
