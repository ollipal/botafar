from abc import ABC, abstractmethod
from inspect import Parameter, signature

from ..constants import KEYS

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
    _blocked_event_keys = set()  # TODO

    def __init__(
        self,
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
        ), "Input cannot be host_only and player_only"
        assert not (
            keyboard_only and screen_only
        ), "Input cannot be host_only and player_only"

        self._keys = keys
        self._sender = SENDER_MAP[(host_only, player_only)]
        self._origin = ORIGIN_MAP[(keyboard_only, screen_only)]
        self._state = start_event.name
        self._latest_event = start_event
        self._alternative_map = {}
        self._state_callbacks = {}
        self._callbacks_added = False

        for key in self._keys:
            self._register_key(key)

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

    def _register_key(self, key):
        assert (
            key in KEYS
        ), f"Unknown key '{key}'"  # TODO add url to allowed keys

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
    def _process_event(self, key, event):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    def _get_callbacks_with_parameters(self, key, event):
        if key in self._alternative_map:
            key = self._alternative_map[key]

        ignore, event = self._process_event(key, event)
        self._state = event.name  # Update state even if no callbacks
        if ignore or event.name not in self._state_callbacks:
            return

        self._latest_event = event
        return self._state_callbacks[event.name]

    def _takes_event(self, function):
        parameters = signature(function).parameters.values()
        takes_event = False
        for i, param in enumerate(parameters):
            if i == 0:
                if param.name == "event":
                    takes_event = True
                elif param.kind == Parameter.POSITIONAL_ONLY:
                    raise RuntimeError(
                        f"The first input callback argument must be called "
                        "'event', or it needs to be optional. Currently it "
                        f"is '{param.name}' and it is required."
                    )
            else:
                if (
                    (
                        param.kind == Parameter.POSITIONAL_OR_KEYWORD
                        and param.default == Parameter.empty
                    )
                    or param.kind  # Reguired positional or keyword argument
                    == Parameter.POSITIONAL_ONLY
                    or (  # Reguired positional argument
                        param.kind == Parameter.KEYWORD_ONLY
                        and param.default == Parameter.empty
                    )  # Required keyword only argument
                ):
                    raise RuntimeError(
                        "Input callback arguments need to be optional, "
                        "except the first one that can be required if it "
                        f"called 'event'. Argument '{param.name}' should be "
                        "made optional or removed."
                    )
        return takes_event

    def _add_state_callback(self, name, function):
        takes_event = self._takes_event(
            function
        )  # Also validates other parameters

        if name in self._state_callbacks:
            self._state_callbacks[name].append((function, takes_event))
        else:
            self._state_callbacks[name] = [(function, takes_event)]

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
