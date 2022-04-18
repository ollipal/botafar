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


class on_prepare(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_prepare", func)
        return func


class on_start(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_start", func)
        return func


class on_stop(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_stop", func)
        return func


class on_stop_immediate(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_stop_immediate", func)
        return func


class on_exit(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_exit", func)
        return func


class on_exit_immediate(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_exit_immediate", func)
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


class on_repeat(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):  # noqa: N805
        pass

    def wrap(self, func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args):
                while True:
                    await func(*args)
                    await sleep_async(0)

        else:

            def wrapper(*args):
                while True:
                    func(*args)
                    sleep(0)

        CallbackBase.register_callback("on_repeat", wrapper)
        return func
