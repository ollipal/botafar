"""botafar"""

__version__ = "0.0.8"


from ._internal.controls import Button, Joystick, Slider
from ._internal.decorators import (
    on_exit,
    on_init,
    on_prepare,
    on_repeat,
    on_start,
    on_stop,
)
from ._internal.decorators import on_time
from ._internal.decorators import on_time as _internal_on_time
from ._internal.exceptions import SleepCancelledError
from ._internal.main import _cli  # This enables `botafar` from cli
from ._internal.main import exit, print, run
from ._internal.states import (
    disable_controls,
    enable_controls,
    player,
    sleep,
    sleep_async,
    state,
    stop,
    time,
)

version = __version__


""" def _internal_get_on_time(time_):
    class on_time(_internal_on_time):  # noqa: N801
        def __init__(self, *func):
            self.time = time_
            super().__init__(*func)

    return on_time


# For autocompletion examples:
on_time_1 = _internal_get_on_time(1)
on_time_2 = _internal_get_on_time(2)
on_time_3 = _internal_get_on_time(3)


# Handle all of the other numbers (on_time_*):
def __getattr__(name):
    if name.startswith("on_time_"):
        time_string = name.replace("on_time_", "")
        try:
            time_ = int(time_string)
        except ValueError:
            raise RuntimeError(
                f"Unknown on_time_*: '{time_string}'. Use integers, "
                "for example: on_time_5"
            )

        return _internal_get_on_time(time_)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
 """
