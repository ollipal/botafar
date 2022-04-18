import asyncio

from ..callbacks import CallbackBase
from ..function_utils import takes_parameter
from ..states import sleep, sleep_async
from .decorator_base import DecoratorBase


class on_init(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func


class on_time(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):  # noqa: N805
        if takes_parameter(params, "time"):
            self.takes_time = True

    def wrap(self, func):
        assert self.time is not None, "Set self.time during __init__"
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args):
                await sleep_async(self.time)
                return await func(*args)

        else:

            def wrapper(*args):
                sleep(self.time)
                return func(*args)

        CallbackBase.register_callback("on_time", wrapper)
        return func
