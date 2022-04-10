"""telebotties"""

__version__ = "0.0.1"


from ._internal.callbacks import (  # on_init,
    on_exit,
    on_prepare,
    on_repeat,
    on_start,
    on_stop,
    on_time,
)

from ._internal.decorators import on_init
from ._internal.controls import Button
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
