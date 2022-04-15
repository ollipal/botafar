from ..function_utils import get_params, takes_parameter
from ..log_formatter import get_logger

logger = get_logger()


class CallbackBase:
    _callbacks = {}
    _instances = {}

    def __init__(self):
        pass

    @staticmethod
    def _get_callbacks(event):
        if event.name not in CallbackBase._callbacks:
            return []

        return CallbackBase._callbacks[event.name]._get_instance_callbacks(
            event
        )

    @staticmethod
    def get_by_name(name):
        if name not in CallbackBase._callbacks:
            return []

        return CallbackBase._callbacks[name]

    @staticmethod
    def register_callback(name, function):
        # NOTE # Also validates other parameters
        if CallbackBase._takes_time(function):
            pass  # The result does not matter, as time is already wrapped in

        if name in CallbackBase._callbacks:
            CallbackBase._callbacks[name].append(function)
        else:
            CallbackBase._callbacks[name] = [function]

        logger.debug(f"{name} registered")

    @staticmethod
    def register_instance(name, function):
        # NOTE # Also validates other parameters
        if CallbackBase._takes_time(function):
            pass  # The result does not matter, as time is already wrapped in

        if name in CallbackBase._callbacks:
            CallbackBase._callbacks[name].append(function)
        else:
            CallbackBase._callbacks[name] = [function]

        logger.debug(f"{name} registered")

    @staticmethod
    def _takes_time(function):
        return takes_parameter(get_params(function), "time")
