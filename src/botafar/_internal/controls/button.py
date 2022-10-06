from ..decorators import DecoratorBase, get_decorator
from ..events import Event
from ..function_utils import get_function_title, takes_parameter
from .control_base import ControlBase


class Button(ControlBase):
    def __init__(
        self,
        key,
        alt=None,
        owner_only=False,
        amount=1,
    ):
        start_event = Event("on_release", "owner", key)
        start_event._set_time(-1)
        start_event._set_active_method(lambda: False)
        self._state = start_event.name

        # TODO why self._keys[0] was undefined inside 'on_release'
        # and this was needed?...
        self._key = key

        class OnPress(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                self._add_key_to_has_callbacks(self._key, title, 3)
                self._add_state_callback("on_press", func)
                return func

        class OnRelease(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                if title is not None:
                    title = f"{title} (release)"
                self._add_key_to_has_callbacks(self._key, title, 1)
                self._add_state_callback("on_release", func)
                return func

        class OnAny(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                if not self._takes_event(func):
                    raise RuntimeError(
                        f"{self_.decorator_name} callback function must take "
                        "'event' as the first parameter."
                    )

                title = self_.func_title
                self._add_key_to_has_callbacks(self._key, title, 2)
                self._add_state_callback("on_press", func)
                self._add_state_callback("on_release", func)
                return func

        self._on_press_class = OnPress
        self._on_release_class = OnRelease
        self._on_any_class = OnAny

        if alt is not None:
            alt = [alt]

        super().__init__(
            "button",
            [key],
            owner_only,
            start_event,
            alt,
            amount,
        )

    def on_press(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_press_class, title, "on_press", True)(
            func
        )

    def on_release(self, func):
        title = get_function_title(func)
        return get_decorator(
            self._on_release_class, title, "on_release", True
        )(func)

    def on_any(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_any_class, title, "on_any", True)(func)

    def _get_release_callbacks_and_event(self, time):
        if self.is_released:
            return [], None

        release_event = self.latest_event
        release_event._set_time(time)
        release_event._change_name("on_release")
        return self._get_instance_callbacks(release_event), release_event

    @property
    def is_pressed(self):
        return self._state == "on_press"

    @property
    def is_released(self):
        return self._state == "on_release"

    def _process_event(self, event):
        """Returns: ignore, updated event"""
        ignore = self._state == event.name
        self._state = event.name
        return ignore, event

    def __repr__(self):
        if self._alt is not None:
            alt_text = f', alt="{self._alt[0]}"'
        else:
            alt_text = ""
        return f'Button("{self._key}"{alt_text}{self._sender_origin_repr()})'
