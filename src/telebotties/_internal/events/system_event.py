import json

from ..constants import SYSTEM_EVENT


class SystemEvent:
    def __init__(self, name, value, text):
        self._name = name
        self._value = value
        self._text = text
        self._type = SYSTEM_EVENT

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

    def _to_json(self):
        return json.dumps(
            {
                "name": self.name,
                "value": self.value,
                "text": self.text,
                "type": self._type,
            }
        )

    def __repr__(self):
        return (
            f"SystemEvent(name='{self.name}', value={self.value}, "
            f"text='{self.text}')"
        )
