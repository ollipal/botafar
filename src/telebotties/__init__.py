"""telebotties"""

__version__ = "0.0.1"


from ._internal.cli import _cli  # This enables `telebotties` from cli
from ._internal.inputs import Button
from ._internal.main import listen

version = __version__