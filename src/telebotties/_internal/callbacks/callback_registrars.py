from ..log_formatter import get_logger
from . import CallbackBase

logger = get_logger()


def on_init(function):
    CallbackBase.register_callback("on_init", function)
    return function


def on_exit(function):
    CallbackBase.register_callback("on_exit", function)
    return function


def on_prepare(function):
    CallbackBase.register_callback("on_prepare", function)
    return function


def on_start(function):
    CallbackBase.register_callback("on_start", function)
    return function


def on_stop(function):
    CallbackBase.register_callback("on_stop", function)
    return function
