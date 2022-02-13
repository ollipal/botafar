from .event import Event
from .input_base import InputBase


class Button(InputBase):
    def __init__(
        self,
        key,
        host_only=False,
        player_only=False,
        keyboard_only=False,
        screen_only=False,
    ):
        start_event = Event("release", False, "host", "keyboard", -1)
        super().__init__(
            [key],
            host_only,
            player_only,
            keyboard_only,
            screen_only,
            start_event,
        )

    def alternative(self, key):
        self._register_alternative_keys([key])

    def on_press(self, function):
        self._add_state_callback("press", function)
        return function

    def on_release(self, function):
        self._add_state_callback("release", function)
        return function

    def on_any(self, function):
        if not self._takes_event(function):
            raise RuntimeError(
                "on_any callback function must take 'event' as the first parameter."
            )

        self._add_state_callback("press", function)
        self._add_state_callback("release", function)
        return function

    @property
    def is_pressed(self):
        return self._state == "press"

    @property
    def is_release(self):
        return self._state == "release"

    @property
    def state(self):
        return self._state

    def _process_event(self, key, event):
        return self._state == event.name, event

    def __repr__(self):
        return f'Button("{self._keys[0]}"{self._sender_origin_repr()})'
