from abc import ABC, abstractmethod

from ..callback_executor import CallbackExecutor
from ..constants import KEYS
from ..function_utils import takes_parameter

# (host_only, player_only)
SENDER_MAP = {
    (False, False): "any",
    (True, False): "host",
    (False, True): "player",
}

# (host_only, player_only)
ORIGIN_MAP = {
    (False, False): "any",
    (True, False): "keyboard",
    (False, True): "screen",
}

SENDER_REPR = {
    "any": "",
    "host": "host_only=True",
    "player": "player_only=True",
}

ORIGIN_REPR = {
    "any": "",
    "keyboard": "keyboard_only=True",
    "screen": "screen_only=True",
}


class InputBase(ABC):
    _event_callbacks = {}
    _inputs = []

    def __init__(
        self,
        type,
        keys,
        host_only,
        player_only,
        keyboard_only,
        screen_only,
        start_event,
    ):
        # TODO makey assertions key makes sense, others type boolean
        # Make sure makes sense
        assert not (
            host_only and player_only
        ), "Input cannot be host_only and player_only at the same time"
        assert not (
            keyboard_only and screen_only
        ), "Input cannot be keyboard_only and screen_only at the same time"

        self._keys = keys
        self._sender = SENDER_MAP[(host_only, player_only)]
        self._origin = ORIGIN_MAP[(keyboard_only, screen_only)]
        self._state = start_event.name
        self._latest_event = start_event
        self._alternative_map = {}
        self._state_callbacks = {}
        self._callbacks_added = False

        for key in self._keys:
            self._register_key(key)  # This first checks all keys are allowed
        assert len(keys) == len(
            set(keys)
        ), "Input cannot have multiple same keys"

        self._data = {
            "type": type,
            "keys": {key: [key] for key in keys},
            "titles": {},
            "has_callbacks": [],
            "without_callbacks": keys,
        }
        InputBase._inputs.append(self)

    @staticmethod
    def _get_input_datas():
        return [input_._data for input_ in InputBase._inputs]

    def _add_key_to_has_callbacks(self, key, title, tier):
        if title is None:
            tier = 0

        if key not in self._data["has_callbacks"]:
            self._data["has_callbacks"].append(key)
            self._data["without_callbacks"].remove(key)

        if (
            key not in self._data["titles"]
            or self._data["titles"][key][1] < tier
        ):
            self._data["titles"][key] = (title, tier)

    @staticmethod
    def _get_callbacks(event):
        event._update(True, -1)  # TODO properly

        if event._callback_key not in InputBase._event_callbacks:
            return []

        return InputBase._event_callbacks[
            event._callback_key
        ]._get_instance_callbacks(event)

    def _register_alternative_keys(self, alternatives):
        if self._callbacks_added:
            raise RuntimeError(
                "alternative() should be used before registering callbacks"
            )

        # TODO make sure can be called only if not listening started and
        # no callbacks has been registered
        assert len(alternatives) == len(self._keys)
        for key, alternative in zip(self._keys, alternatives):
            self._register_key(alternative)
            self._alternative_map[alternative] = key
            self._data["keys"][key].append(alternative)

    def _register_key(self, key):
        if key not in KEYS:
            if isinstance(key, str) and key.upper() in KEYS:
                raise RuntimeError(
                    f"Unknown key '{key}', did you mean '{key.upper()}'?"
                )
            else:
                raise RuntimeError(
                    f"Unknown key '{key}'"
                )  # TODO link to allowed keys

        new_event_callback_keys = self._get_event_callback_keys(
            key, self._sender, self._origin
        )
        for callback_key in new_event_callback_keys:
            if callback_key in self._event_callbacks:
                raise RuntimeError(
                    f"Cannot create {self}. "
                    f"{self._event_callbacks[callback_key]} already handles "
                    "some of the same input events. Only one input can "
                    "handle each Event."
                )
            self._event_callbacks[callback_key] = self

    @property
    def latest_event(self):
        return self._latest_event

    @abstractmethod  # Each input needs unique docstring
    def state(self):
        pass

    @abstractmethod
    def _process_event(self, event):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    def _get_instance_callbacks(self, event):
        if event._key in self._alternative_map:
            event._key = self._alternative_map[event._key]

        ignore, event = self._process_event(event)
        self._state = event.name  # Update state even if no callbacks
        if ignore or event.name not in self._state_callbacks:
            return []

        self._latest_event = event
        return self._state_callbacks[event.name]

    @staticmethod
    def _takes_event(function):
        return takes_parameter(function, "event")

    def _add_state_callback(self, name, function):
        if self._takes_event(function):  # Also validates other parameters
            CallbackExecutor.add_to_takes_event(function)

        if name in self._state_callbacks:
            self._state_callbacks[name].append(function)
        else:
            self._state_callbacks[name] = [function]

        self._callbacks_added = True

    def _sender_origin_repr(self):
        sender_repr = SENDER_REPR[self._sender]
        origin_repr = ORIGIN_REPR[self._origin]

        if sender_repr == "" and origin_repr == "":
            return ""
        elif sender_repr != "" and origin_repr != "":  # Space required
            return f", {sender_repr}, {origin_repr}"
        else:
            return f", {sender_repr}{origin_repr}"

    def _get_event_callback_keys(self, key, sender, origin):
        if sender == "any" and origin == "any":
            return [
                (key, "host", "keyboard"),
                (key, "player", "keyboard"),
                (key, "host", "screen"),
                (key, "player", "screen"),
            ]
        elif sender == "host" and origin == "any":
            return [
                (key, "host", "keyboard"),
                (key, "host", "screen"),
            ]
        elif sender == "player" and origin == "any":
            return [
                (key, "player", "keyboard"),
                (key, "player", "screen"),
            ]
        elif sender == "any" and origin == "keyboard":
            return [
                (key, "host", "keyboard"),
                (key, "player", "keyboard"),
            ]
        elif sender == "host" and origin == "keyboard":
            return [
                (key, "host", "keyboard"),
            ]
        elif sender == "player" and origin == "keyboard":
            return [
                (key, "player", "keyboard"),
            ]
        elif sender == "any" and origin == "screen":
            return [
                (key, "host", "screen"),
                (key, "player", "screen"),
            ]
        elif sender == "host" and origin == "screen":
            return [
                (key, "host", "screen"),
            ]
        elif sender == "player" and origin == "screen":
            return [
                (key, "player", "screen"),
            ]
        else:
            RuntimeError("This should not happen")
