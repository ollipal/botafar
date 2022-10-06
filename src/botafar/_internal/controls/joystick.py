from ..decorators import DecoratorBase, get_decorator
from ..events import Event
from ..function_utils import get_function_title, takes_parameter
from ..log_formatter import get_logger
from .control_base import ControlBase

logger = get_logger()

DIRECTIONS = {
    (-1, -1): "on_down_left",
    (-1, 0): "on_left",
    (-1, 1): "on_up_left",
    (0, -1): "on_down",
    (0, 0): "on_center",
    (0, 1): "on_up",
    (1, -1): "on_down_right",
    (1, 0): "on_right",
    (1, 1): "on_up_right",
}

DIAGONALS = {"on_down_left", "on_up_left", "on_down_right", "on_up_right"}

# in None case prefer horizontal...
# Should not happen, maybe at all?
DIAGONAL_RESOLVERS = {
    (None, "on_down_left"): "on_left",
    (None, "on_up_left"): "on_left",
    (None, "on_down_right"): "on_right",
    (None, "on_up_right"): "on_right",
    ("vertical", "on_down_left"): "on_left",
    ("vertical", "on_up_left"): "on_left",
    ("vertical", "on_down_right"): "on_right",
    ("vertical", "on_up_right"): "on_right",
    ("horizontal", "on_down_left"): "on_down",
    ("horizontal", "on_up_left"): "on_up",
    ("horizontal", "on_down_right"): "on_down",
    ("horizontal", "on_up_right"): "on_up",
}


# NOTE: all changes here should be reflected on frontend as well
def parse_is_down(is_down, has_diagonals, latest_update_direction):
    # Get horizontal, vertical values
    if is_down["up"] and not is_down["down"]:
        vertical_value = 1
    elif not is_down["up"] and is_down["down"]:
        vertical_value = -1
    else:  # Both or neither
        vertical_value = 0

    if is_down["left"] and not is_down["right"]:
        horizontal_value = -1
    elif not is_down["left"] and is_down["right"]:
        horizontal_value = 1
    else:  # Both or neither
        horizontal_value = 0

    # Parse new direction
    direction = DIRECTIONS[horizontal_value, vertical_value]

    # Modify if diagonal and cannot be
    if direction in DIAGONALS and not has_diagonals:
        direction = DIAGONAL_RESOLVERS[latest_update_direction, direction]

    # Update update direction state
    new_update_direction = None
    if not has_diagonals:
        if direction == "on_center":
            new_update_direction = None
        elif direction in ["on_up", "on_down"]:
            new_update_direction = "vertical"
        elif direction in ["on_left", "on_right"]:
            new_update_direction = "horizontal"
        else:
            raise RuntimeError("Should not happen")

    return direction, new_update_direction


class Joystick(ControlBase):
    def __init__(  # noqa: C901
        self,
        up_key,
        left_key,
        down_key,
        right_key,
        diagonals=False,
        alt=None,
        owner_only=False,
        amount=1,
    ):
        start_event = Event("on_center", "owner", up_key)
        start_event._set_time(-1)
        start_event._set_active_method(lambda: False)

        class OnCenter(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                if title is not None:
                    title = f"{title} (release)"
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 1)
                self._add_key_to_has_callbacks(self._keys_copy[1], title, 1)
                self._add_key_to_has_callbacks(self._keys_copy[2], title, 1)
                self._add_key_to_has_callbacks(self._keys_copy[3], title, 1)
                self._add_state_callback("on_center", func)
                return func

        class OnUp(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 3)
                self._add_state_callback("on_up", func)
                return func

        class OnLeft(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[1], title, 3)
                self._add_state_callback("on_left", func)
                return func

        class OnDown(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[2], title, 3)
                self._add_state_callback("on_down", func)
                return func

        class OnRight(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[3], title, 3)
                self._add_state_callback("on_right", func)
                return func

        class OnUpLeft(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                self._change_type("joystick8")
                self._has_diagonals = True

                title = self_.func_title
                if title is not None:
                    title = f"{title} (combination)"
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 0)
                self._add_state_callback("on_up_left", func)
                return func

        class OnDownLeft(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                self._change_type("joystick8")
                self._has_diagonals = True

                title = self_.func_title
                if title is not None:
                    title = f"{title} (combination)"
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 0)
                self._add_state_callback("on_down_left", func)
                return func

        class OnDownRight(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                self._change_type("joystick8")
                self._has_diagonals = True

                title = self_.func_title
                if title is not None:
                    title = f"{title} (combination)"
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 0)
                self._add_state_callback("on_down_right", func)
                return func

        class OnUpRight(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                self._change_type("joystick8")
                self._has_diagonals = True

                title = self_.func_title
                if title is not None:
                    title = f"{title} (combination)"
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 0)
                self._add_state_callback("on_up_right", func)
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
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 2)
                self._add_key_to_has_callbacks(self._keys_copy[1], title, 2)
                self._add_key_to_has_callbacks(self._keys_copy[2], title, 2)
                self._add_key_to_has_callbacks(self._keys_copy[3], title, 2)
                self._add_state_callback("on_center", func)
                self._add_state_callback("on_up", func)
                self._add_state_callback("on_left", func)
                self._add_state_callback("on_down", func)
                self._add_state_callback("on_right", func)
                self._add_state_callback("on_up_left", func)
                self._add_state_callback("on_down_left", func)
                self._add_state_callback("on_down_right", func)
                self._add_state_callback("on_up_right", func)
                return func

        self._on_center_class = OnCenter
        self._on_up_class = OnUp
        self._on_left_class = OnLeft
        self._on_down_class = OnDown
        self._on_right_class = OnRight
        self._on_up_left_class = OnUpLeft
        self._on_down_left_class = OnDownLeft
        self._on_down_right_class = OnDownRight
        self._on_up_right_class = OnUpRight
        self._on_any_class = OnAny

        # Some keys keeps getting missing from _keys... This is a workaround.
        self._keys_copy = [up_key, left_key, down_key, right_key]
        self._has_diagonals = False

        # Get the initial state
        self._reset_state()

        super().__init__(
            "joystick4",
            [up_key, left_key, down_key, right_key],
            owner_only,
            start_event,
            alt,
            amount,
        )

        if diagonals:
            self._change_type("joystick8")
            self._has_diagonals = True

    def on_center(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_center_class, title, "on_center", True)(
            func
        )

    def on_up(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_up_class, title, "on_up", True)(func)

    def on_left(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_left_class, title, "on_left", True)(func)

    def on_down(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_down_class, title, "on_down", True)(func)

    def on_right(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_right_class, title, "on_right", True)(
            func
        )

    def on_up_left(self, func):
        title = get_function_title(func)
        return get_decorator(
            self._on_up_left_class, title, "on_up_left", True
        )(func)

    def on_down_left(self, func):
        title = get_function_title(func)
        return get_decorator(
            self._on_down_left_class, title, "on_down_left", True
        )(func)

    def on_down_right(self, func):
        title = get_function_title(func)
        return get_decorator(
            self._on_down_right_class, title, "on_down_right", True
        )(func)

    def on_up_right(self, func):
        title = get_function_title(func)
        return get_decorator(
            self._on_up_right_class, title, "on_up_right", True
        )(func)

    def on_any(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_any_class, title, "on_any", True)(func)

    def _reset_state(self):
        self._latest_update_direction = None
        self._is_down = {
            "up": False,
            "left": False,
            "down": False,
            "right": False,
        }
        self._state = "on_center"

    def _get_release_callbacks_and_event(self, time):
        no_release_cbs = self.is_center

        if no_release_cbs:
            return [], None

        release_event = self.latest_event
        release_event._set_time(time)
        # NOTE: this will change to on_center during _process_event()
        release_event._change_name("on_release")
        return self._get_instance_callbacks(release_event), release_event

    @property
    def is_center(self):
        return self._state == "on_center"

    @property
    def is_up(self):
        return self._state == "on_up"

    @property
    def is_left(self):
        return self._state == "on_left"

    @property
    def is_down(self):
        return self._state == "on_down"

    @property
    def is_right(self):
        return self._state == "on_right"

    @property
    def is_up_left(self):
        return self._state == "on_up_left"

    @property
    def is_down_left(self):
        return self._state == "on_down_left"

    @property
    def is_down_right(self):
        return self._state == "on_down_right"

    @property
    def is_up_right(self):
        return self._state == "on_up_right"

    def _process_event(self, event):  # noqa:C901
        """Returns: ignore, updated event"""

        # Update is down state, get direction
        if event.name in ["on_release", "on_press"]:
            if event.name == "on_release":
                if event._key == self._keys_copy[0]:
                    self._is_down["up"] = False
                elif event._key == self._keys_copy[1]:
                    self._is_down["left"] = False
                elif event._key == self._keys_copy[2]:
                    self._is_down["down"] = False
                elif event._key == self._keys_copy[3]:
                    self._is_down["right"] = False
                else:
                    raise RuntimeError("Should not happen")
            elif event.name == "on_press":
                if event._key == self._keys_copy[0]:
                    self._is_down["up"] = True
                elif event._key == self._keys_copy[1]:
                    self._is_down["left"] = True
                elif event._key == self._keys_copy[2]:
                    self._is_down["down"] = True
                elif event._key == self._keys_copy[3]:
                    self._is_down["right"] = True
                else:
                    raise RuntimeError("Should not happen")
            else:
                raise RuntimeError("Should not happen")

            direction, new_update_direction = parse_is_down(
                self._is_down,
                self._has_diagonals,
                self._latest_update_direction,
            )
            self._latest_update_direction = new_update_direction

        else:
            if event.name == "on_center":
                self._is_down = {
                    "up": False,
                    "left": False,
                    "down": False,
                    "right": False,
                }
            elif event.name == "on_up":
                self._is_down = {
                    "up": True,
                    "left": False,
                    "down": False,
                    "right": False,
                }
            elif event.name == "on_left":
                self._is_down = {
                    "up": False,
                    "left": True,
                    "down": False,
                    "right": False,
                }
            elif event.name == "on_down":
                self._is_down = {
                    "up": False,
                    "left": False,
                    "down": True,
                    "right": False,
                }
            elif event.name == "on_right":
                self._is_down = {
                    "up": False,
                    "left": False,
                    "down": False,
                    "right": True,
                }
            elif event.name == "on_up_left":
                self._is_down = {
                    "up": True,
                    "left": True,
                    "down": False,
                    "right": False,
                }
            elif event.name == "on_down_left":
                self._is_down = {
                    "up": False,
                    "left": True,
                    "down": True,
                    "right": False,
                }
            elif event.name == "on_down_right":
                self._is_down = {
                    "up": False,
                    "left": False,
                    "down": True,
                    "right": True,
                }
            elif event.name == "on_up_right":
                self._is_down = {
                    "up": True,
                    "left": False,
                    "down": False,
                    "right": True,
                }
            else:
                raise RuntimeError("Should not happen")

            direction = event.name

        # Ignore if the same as latest
        ignore = direction == self._state

        # Update state and event if not ignoring
        if not ignore:
            self._state = direction
            event._name = direction

        return ignore, event

    def __repr__(self):
        if self._alt is not None:
            alt_text = (
                f', alt=["{self._alt[0]}","{self._alt[1]}",'
                f'"{self._alt[2]}","{self._alt[3]}"]'
            )
        else:
            alt_text = ""
        return (
            f'Joystick("{self._keys_copy[0]}","{self._keys_copy[1]}",'
            f'"{self._keys_copy[2]}","{self._keys_copy[3]}"{alt_text}'
            f"{self._sender_origin_repr()})"
        )
