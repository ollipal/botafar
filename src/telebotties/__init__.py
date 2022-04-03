"""telebotties"""

__version__ = "0.0.1"


from ._internal.callbacks import (
    on_exit,
    on_init,
    on_prepare,
    on_start,
    on_stop,
)
from ._internal.inputs import Button
from ._internal.main import _cli  # This enables `telebotties` from cli
from ._internal.main import listen, print, exit
from ._internal.states import state, enable_controls, disable_controls, stop

version = __version__
