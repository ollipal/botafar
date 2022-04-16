"""telebotties"""

__version__ = "0.0.1"


from ._internal.callbacks import (  # on_init,; on_time,
    on_exit,
    on_prepare,
    on_repeat,
    on_start,
    on_stop,
)
from ._internal.controls import Button
from ._internal.decorators import on_init
from ._internal.exceptions import SleepCancelledError
from ._internal.main import _cli  # This enables `telebotties` from cli
from ._internal.main import exit, listen, print
from ._internal.states import (
    disable_controls,
    enable_controls,
    host,
    player,
    sleep,
    sleep_async,
    state,
    stop,
    time,
)

version = __version__

from ._internal.callbacks import on_time

# For autocompletion examples:
on_time_1 = on_time
on_time_2 = on_time
on_time_3 = on_time
on_time_4 = on_time
on_time_5 = on_time
""" on_time_6 = on_time
on_time_7 = on_time
on_time_8 = on_time
on_time_9 = on_time
on_time_11 = on_time
on_time_12 = on_time
on_time_13 = on_time
on_time_14 = on_time
on_time_15 = on_time
on_time_16 = on_time
on_time_17 = on_time
on_time_18 = on_time
on_time_19 = on_time
on_time_20 = on_time
on_time_21 = on_time
on_time_22 = on_time
on_time_23 = on_time
on_time_24 = on_time
on_time_25 = on_time
on_time_26 = on_time
on_time_27 = on_time
on_time_28 = on_time
on_time_29 = on_time
on_time_30 = on_time
on_time_31 = on_time
on_time_32 = on_time
on_time_33 = on_time
on_time_34 = on_time
on_time_35 = on_time
on_time_36 = on_time
on_time_37 = on_time
on_time_38 = on_time
on_time_39 = on_time
on_time_40 = on_time
on_time_41 = on_time
on_time_42 = on_time
on_time_43 = on_time
on_time_44 = on_time
on_time_45 = on_time
on_time_46 = on_time
on_time_47 = on_time
on_time_48 = on_time
on_time_49 = on_time
on_time_50 = on_time
on_time_51 = on_time
on_time_52 = on_time
on_time_53 = on_time
on_time_54 = on_time
on_time_55 = on_time
on_time_56 = on_time
on_time_57 = on_time
on_time_58 = on_time
on_time_59 = on_time
on_time_60 = on_time """
# Handle all of the other numbers (on_time_*):
def __getattr__(name):
    if name.startswith("on_time_"):
        time_string = name.replace("on_time_", "")
        try:
            time = int(time_string)
        except ValueError:
            raise RuntimeError(
                f"Unknown on_time_*: '{time_string}'. Use ints, for example: on_time_5"
            )

        from ._internal.callbacks import on_time

        return on_time
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
