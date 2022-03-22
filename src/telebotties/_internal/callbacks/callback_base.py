from ..callback_executor import CallbackExecutor
from ..function_utils import takes_parameter
from ..log_formatter import get_logger

logger = get_logger()


class CallbackBase:
    _callbacks = {}

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
        # TODO should not check takes time every time...
        if CallbackBase._takes_time(
            function
        ):  # Also validates other parameters
            # NOTE: can be added here even if not time event
            # This dies not matter as long as time is not passed to
            # CallbackExecutor
            CallbackExecutor.add_to_takes_time(function)

        if name in CallbackBase._callbacks:
            CallbackBase._callbacks[name].append(function)
        else:
            CallbackBase._callbacks[name] = [function]

        logger.debug(f"{name} registered")

    @staticmethod
    def _takes_time(function):
        return takes_parameter(function, "time")
