from ..events import Event
from ..function_utils import get_function_name
from .input_base import InputBase


class Button(InputBase):
    def __init__(
        self,
        key,
        alternative=None,
        host_only=False,
        player_only=False,
        amount=1,
    ):
        start_event = Event("on_release", "host", key)
        start_event._set_time(-1)
        start_event._set_active_method(lambda: False)

        # TODO why self._keys[0] was undefined inside 'on_release'
        # and this was needed?...
        self._key = key
        super().__init__(
            "Button",
            [key],
            host_only,
            player_only,
            start_event,
            alternative,
            amount,
        )

    def on_press(self, function):
        title = get_function_name(function)
        self._add_key_to_has_callbacks(self._key, title, 3)
        self._add_state_callback("on_press", function)
        return function

    def on_release(self, function):
        title = get_function_name(function)
        self._add_key_to_has_callbacks(self._key, f"{title} (release)", 1)
        self._add_state_callback("on_release", function)
        return function

    def on_any(self, function):
        if not self._takes_event(function):
            raise RuntimeError(
                "on_any callback function must take 'event'"
                " as the first parameter."
            )

        title = get_function_name(function)
        self._add_key_to_has_callbacks(self._key, title, 2)
        self._add_state_callback("on_press", function)
        self._add_state_callback("on_release", function)
        return function

    @property
    def is_pressed(self):
        return self._state == "on_press"

    @property
    def is_released(self):
        return self._state == "on_release"

    @property
    def state(self):
        return self._state

    def _process_event(self, event):
        """Returns: ignore, updated event"""
        return self._state == event.name, event

    def __repr__(self):
        return f'Button("{self._keys[0]}"{self._sender_origin_repr()})'
