from ..decorators import DecoratorBase, get_decorator
from ..events import Event
from ..function_utils import get_function_title, takes_parameter
from ..log_formatter import get_logger
from .control_base import ControlBase

logger = get_logger()

KEY_ROWS = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"],
]

KEY_COLUMNS = [
    ["Q", "A", "Z"],
    ["W", "S", "X"],
    ["E", "D", "C"],
    ["R", "F", "V"],
    ["T", "G", "B"],
    ["Y", "H", "N"],
    ["U", "J", "M"],
    ["I", "K"],
    ["O", "L"],
    # ["P"]
]

DIRECTIONS = {
    ("slider_horizontal", -1): "on_left",
    ("slider_horizontal", 0): "on_center",
    ("slider_horizontal", 1): "on_right",
    ("slider_vertical", -1): "on_up",
    ("slider_vertical", 0): "on_center",
    ("slider_vertical", 1): "on_down",
}


def quess_slider_type(up_or_left_key, down_or_right_key, alt):  # noqa:C901
    """An over engineered way to quess a Slider orientation :D"""

    if alt is not None and len(alt) == 2:
        alt_up_or_left_key = alt[0]
        alt_down_or_right_key = alt[1]
    else:
        alt_up_or_left_key = None
        alt_down_or_right_key = None

    # Handle arrow cases
    if (up_or_left_key == "LEFT" and down_or_right_key == "RIGHT") or (
        alt_up_or_left_key == "LEFT" and alt_down_or_right_key == "RIGHT"
    ):
        return "slider_horizontal"
    elif (up_or_left_key == "UP" and down_or_right_key == "DOWN") or (
        alt_up_or_left_key == "UP" and alt_down_or_right_key == "DOWN"
    ):
        return "slider_vertical"

    # Guess space always to be the bottom one if last
    if down_or_right_key == "SPACE" or alt_down_or_right_key == "SPACE":
        return "slider_vertical"

    # Check if keys are on the same row or column in a typical keyboard
    for row in KEY_ROWS:
        if up_or_left_key in row and down_or_right_key in row:
            if row.index(up_or_left_key) < row.index(down_or_right_key):
                return "slider_horizontal"
        elif alt_up_or_left_key in row and alt_down_or_right_key in row:
            if row.index(alt_up_or_left_key) < row.index(
                alt_down_or_right_key
            ):
                return "slider_horizontal"

    for col in KEY_COLUMNS:
        if up_or_left_key in col and down_or_right_key in col:
            if col.index(up_or_left_key) < col.index(down_or_right_key):
                return "slider_vertical"
        elif alt_up_or_left_key in col and alt_down_or_right_key in col:
            if col.index(alt_up_or_left_key) < col.index(
                alt_down_or_right_key
            ):
                return "slider_vertical"

    # Then let's force some non-random quess:

    # Let's handle if directions mixed
    # (don't care about index, but the same row or column)
    for row in KEY_ROWS:
        if up_or_left_key in row and down_or_right_key in row:
            return "slider_horizontal"
        elif alt_up_or_left_key in row and alt_down_or_right_key in row:
            return "slider_horizontal"

    for col in KEY_COLUMNS:
        if up_or_left_key in col and down_or_right_key in col:
            return "slider_vertical"
        elif alt_up_or_left_key in col and alt_down_or_right_key in col:
            return "slider_vertical"

    # Let's force something if both are reqular keys
    up_or_left_key_row_num = None
    down_or_right_key_row_num = None
    alt_up_or_left_key_row_num = None
    alt_down_or_right_key_row_num = None

    for i, row in enumerate(KEY_ROWS):
        if up_or_left_key in row:
            up_or_left_key_row_num = i
        elif down_or_right_key in row:
            down_or_right_key_row_num = i
        elif alt_up_or_left_key in row:
            alt_up_or_left_key_row_num = i
        elif alt_down_or_right_key in row:
            alt_down_or_right_key_row_num = i

    if (
        up_or_left_key_row_num is not None
        and down_or_right_key_row_num is not None
        and up_or_left_key_row_num < down_or_right_key_row_num
    ):
        return "slider_vertical"
    elif (
        alt_up_or_left_key_row_num is not None
        and alt_down_or_right_key_row_num is not None
        and alt_up_or_left_key_row_num < alt_down_or_right_key_row_num
    ):
        return "slider_vertical"

    up_or_left_key_col_num = None
    down_or_right_key_col_num = None
    alt_up_or_left_key_col_num = None
    alt_down_or_right_key_col_num = None

    for i, col in enumerate(KEY_COLUMNS):
        if up_or_left_key in col:
            up_or_left_key_col_num = i
        elif down_or_right_key in col:
            down_or_right_key_col_num = i
        elif alt_up_or_left_key in col:
            alt_up_or_left_key_col_num = i
        elif alt_down_or_right_key in col:
            alt_down_or_right_key_col_num = i

    if (
        up_or_left_key_col_num is not None
        and down_or_right_key_col_num is not None
        and up_or_left_key_col_num < down_or_right_key_col_num
    ):
        return "slider_horizontal"
    elif (
        alt_up_or_left_key_col_num is not None
        and alt_down_or_right_key_col_num is not None
        and alt_up_or_left_key_col_num < alt_down_or_right_key_col_num
    ):
        return "slider_horizontal"

    # != instead of <
    if (
        up_or_left_key_row_num is not None
        and down_or_right_key_row_num is not None
        and up_or_left_key_row_num != down_or_right_key_row_num
    ):
        return "slider_vertical"
    elif (
        alt_up_or_left_key_row_num is not None
        and alt_down_or_right_key_row_num is not None
        and alt_up_or_left_key_row_num != alt_down_or_right_key_row_num
    ):
        return "slider_vertical"
    elif (
        up_or_left_key_col_num is not None
        and down_or_right_key_col_num is not None
        and up_or_left_key_col_num != down_or_right_key_col_num
    ):
        return "slider_horizontal"
    elif (
        alt_up_or_left_key_col_num is not None
        and alt_down_or_right_key_col_num is not None
        and alt_up_or_left_key_col_num != alt_down_or_right_key_col_num
    ):
        return "slider_horizontal"

    # Let's force some quess if any arrows
    if "RIGHT" in [
        up_or_left_key,
        down_or_right_key,
        alt_up_or_left_key,
        alt_down_or_right_key,
    ] or "LEFT" in [
        up_or_left_key,
        down_or_right_key,
        alt_up_or_left_key,
        alt_down_or_right_key,
    ]:
        return "slider_horizontal"
    elif "UP" in [
        up_or_left_key,
        down_or_right_key,
        alt_up_or_left_key,
        alt_down_or_right_key,
    ] or "DOWN" in [
        up_or_left_key,
        down_or_right_key,
        alt_up_or_left_key,
        alt_down_or_right_key,
    ]:
        return "slider_vertical"

    # Let's force some quess if space
    if "SPACE" in [
        up_or_left_key,
        down_or_right_key,
        alt_up_or_left_key,
        alt_down_or_right_key,
    ]:
        return "slider_vertical"

    # There should not be any other options (except illegal input)
    print(
        "Could not quess a Slider direction!!! This should not happen"
    )  # logger does not work yet
    return "slider_horizontal"


class Slider(ControlBase):
    def __init__(  # noqa: C901
        self,
        up_or_left_key,
        down_or_right_key,
        alt=None,
        orientation=None,
        owner_only=False,
        amount=1,
    ):
        assert orientation in [None, "horizontal", "vertical"]
        self._orientation = orientation

        start_event = Event("on_center", "owner", up_or_left_key)
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
                self._add_state_callback("on_center", func)
                return func

        class OnUp(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                assert (
                    self._type_known is False
                    or self._data["type"] == "slider_vertical"
                ), (
                    "Slider cannot have both horizontal (on_left, on_right)"
                    " and vertical (on_up, on_down) callbacks"
                )
                assert self._orientation != "horizontal", (
                    "A horizontal Slider cannot have on_up callbacks "
                    '(remove orientation="horizontal" or use on_left/'
                    "on_right callback instead)"
                )
                self._change_type("slider_vertical")
                self._type_known = True

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
                assert (
                    self._type_known is False
                    or self._data["type"] == "slider_horizontal"
                ), (
                    "Slider cannot have both horizontal (on_left, on_right)"
                    " and vertical (on_up, on_down) callbacks"
                )
                assert self._orientation != "vertical", (
                    "A vertical Slider cannot have on_left callbacks (remove"
                    ' orientation="vertical" or use on_up/'
                    "on_down callback instead)"
                )

                self._change_type("slider_horizontal")
                self._type_known = True

                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[0], title, 3)
                self._add_state_callback("on_left", func)
                return func

        class OnDown(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                assert (
                    self._type_known is False
                    or self._data["type"] == "slider_vertical"
                ), (
                    "Slider cannot have both horizontal (on_left, on_right)"
                    " and vertical (on_up, on_down) callbacks"
                )
                assert self._orientation != "horizontal", (
                    "A horizontal Slider cannot have on_down callbacks "
                    '(remove orientation="horizontal" or use on_left/'
                    "on_right callback instead)"
                )
                self._change_type("slider_vertical")
                self._type_known = True

                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[1], title, 3)
                self._add_state_callback("on_down", func)
                return func

        class OnRight(DecoratorBase):
            def verify_params_and_set_flags(self_, params):  # noqa: N805
                if takes_parameter(
                    params, "event", error_name=self_.decorator_name
                ):
                    self_.takes_event = True

            def wrap(self_, func):  # noqa: N805
                assert (
                    self._type_known is False
                    or self._data["type"] == "slider_horizontal"
                ), (
                    "Slider cannot have both horizontal (on_left, "
                    "on_right) and vertical (on_up, on_down) callbacks"
                )
                assert self._orientation != "vertical", (
                    "A vertical Slider cannot have on_right callbacks (remove"
                    ' orientation="vertical" or use on_up/on_down'
                    " callback instead)"
                )
                self._change_type("slider_horizontal")
                self._type_known = True

                title = self_.func_title
                self._add_key_to_has_callbacks(self._keys_copy[1], title, 3)
                self._add_state_callback("on_right", func)
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
                self._add_state_callback("on_center", func)
                self._add_state_callback("on_up", func)
                self._add_state_callback("on_left", func)
                self._add_state_callback("on_down", func)
                self._add_state_callback("on_right", func)
                return func

        self._on_center_class = OnCenter
        self._on_up_class = OnUp
        self._on_left_class = OnLeft
        self._on_down_class = OnDown
        self._on_right_class = OnRight
        self._on_any_class = OnAny

        # Some keys keeps getting missing from _keys... This is a workaround.
        self._keys_copy = [up_or_left_key, down_or_right_key]

        # Get the initial state
        self._reset_state()
        self._type_known = False

        if orientation == "horizontal":
            slider_type = "slider_horizontal"
        elif orientation == "vertical":
            slider_type = "slider_vertical"
        else:
            slider_type = quess_slider_type(
                up_or_left_key, down_or_right_key, alt
            )

        super().__init__(
            slider_type,
            [up_or_left_key, down_or_right_key],
            owner_only,
            start_event,
            alt,
            amount,
        )

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

    def on_any(self, func):
        title = get_function_title(func)
        return get_decorator(self._on_any_class, title, "on_any", True)(func)

    def _reset_state(self):
        self._latest_update_direction = None
        self._is_down = {
            "up_or_left": False,
            "down_or_right": False,
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

    def _process_event(self, event):  # noqa:C901
        """Returns: ignore, updated event"""

        # Update is down state, get direction
        if event.name in ["on_release", "on_press"]:
            if event.name == "on_release":
                if event._key == self._keys_copy[0]:
                    self._is_down["up_or_left"] = False
                elif event._key == self._keys_copy[1]:
                    self._is_down["down_or_right"] = False
                else:
                    raise RuntimeError("Should not happen")
            elif event.name == "on_press":
                if event._key == self._keys_copy[0]:
                    self._is_down["up_or_left"] = True
                elif event._key == self._keys_copy[1]:
                    self._is_down["down_or_right"] = True
                else:
                    raise RuntimeError("Should not happen")
            else:
                raise RuntimeError("Should not happen")

            # Get numerical value
            if (
                self._is_down["up_or_left"]
                and not self._is_down["down_or_right"]
            ):
                numerical_value = -1
            elif (
                not self._is_down["up_or_left"]
                and self._is_down["down_or_right"]
            ):
                numerical_value = 1
            else:  # Both or neither
                numerical_value = 0

            # Parse new direction
            direction = DIRECTIONS[self._data["type"], numerical_value]
        else:
            if event.name == "on_center":
                self._is_down = {
                    "up_or_left": False,
                    "down_or_right": False,
                }
            elif event.name in ["on_up", "on_left"]:
                self._is_down = {
                    "up_or_left": True,
                    "down_or_right": False,
                }
            elif event.name in ["on_down", "on_right"]:
                self._is_down = {
                    "up_or_left": False,
                    "down_or_right": True,
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
            alt_text = f', alt=["{self._alt[0]}","{self._alt[1]}"]'
        else:
            alt_text = ""
        return (
            f'Slider("{self._keys_copy[0]}","{self._keys_copy[1]}"{alt_text}'
            f"{self._sender_origin_repr()})"
        )
