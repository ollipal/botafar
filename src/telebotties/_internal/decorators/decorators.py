import asyncio

from ..callbacks import CallbackBase
from ..function_utils import takes_parameter
from ..states import sleep, sleep_async
from .decorator_base import DecoratorBase, get_decorator


class on_init(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func


on_init = get_decorator(on_init, True)


class on_prepare(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_prepare", func)
        return func


on_prepare = get_decorator(on_prepare, True)


class on_start(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_start", func)
        return func


on_start = get_decorator(on_start, True)


class on_stop(DecoratorBase):  # noqa: N801
    def __init__(self, *args, **kwargs):
        assert len(args) == 1 and (
            len(kwargs) == 0 or (len(kwargs) == 1 and "immediate" in kwargs)
        ), (
            "Only a function and a keyword parameter 'immediate' can be "
            f"passed to {self.__class__.__name__}"
        )
        if "immediate" in kwargs and kwargs["immediate"] is True:
            self.immediate = True
        else:
            self.immediate = False

        super().__init__(*args, **kwargs)

    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        if self.immediate:
            CallbackBase.register_callback("on_stop(immediate=True)", func)
        else:
            CallbackBase.register_callback("on_stop", func)
        return func


on_stop = get_decorator(on_stop, False)


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
        CallbackBase.register_callback("on_exit(immediate=True)", func)
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
