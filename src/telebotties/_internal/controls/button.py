from ..decorators import DecoratorBase
from ..events import Event
from ..function_utils import takes_parameter
from .control_base import ControlBase


class Button(ControlBase):
    def __init__(
        self,
        key,
        alternative=None,
        host_only=False,
        amount=1,
    ):
        start_event = Event("on_release", "host", key)
        start_event._set_time(-1)
        start_event._set_active_method(lambda: False)

        # TODO why self._keys[0] was undefined inside 'on_release'
        # and this was needed?...
        self._key = key

        class on_press(DecoratorBase):  # noqa: N801
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(params, "event"):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_name
                self._add_key_to_has_callbacks(self._key, title, 3)
                self._add_state_callback("on_press", func)
                return func

        class on_release(DecoratorBase):  # noqa: N801
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(params, "event"):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_name
                self._add_key_to_has_callbacks(
                    self._key, f"{title} (release)", 1
                )
                self._add_state_callback("on_release", func)
                return func

        class on_any(DecoratorBase):  # noqa: N801
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(params, "event"):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                if not self._takes_event(func):
                    raise RuntimeError(
                        "on_any callback function must take 'event'"
                        " as the first parameter."
                    )

                title = self_.func_name
                self._add_key_to_has_callbacks(self._key, title, 2)
                self._add_state_callback("on_press", func)
                self._add_state_callback("on_release", func)
                return func

        self.on_press = on_press
        self.on_release = on_release
        self.on_any = on_any

        super().__init__(
            "Button",
            [key],
            host_only,
            start_event,
            alternative,
            amount,
        )

    @property
    def is_pressed(self):
        return self._state == "on_press"

    @property
    def is_released(self):
        return self._state == "on_release"

    def _process_event(self, event):
        """Returns: ignore, updated event"""
        return self._state == event.name, event

    def __repr__(self):
        return f'Button("{self._key}"{self._sender_origin_repr()})'
