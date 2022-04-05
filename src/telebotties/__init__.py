"""telebotties"""

__version__ = "0.0.1"


from ._internal.callbacks import (
    on_exit,
    on_init,
    on_prepare,
    on_start,
    on_stop,
)
from ._internal.exceptions import SleepCancelledError
from ._internal.inputs import Button
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
