import asyncio

from ..callbacks import CallbackBase
from ..function_utils import takes_parameter
from ..states import sleep, sleep_async
from .decorator_base import DecoratorBase, get_decorator


class OnInit(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func


def on_init(func):
    return get_decorator(OnInit, "on_init", True)(func)


class OnPrepare(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_prepare", func)
        return func


def on_prepare(func):
    return get_decorator(OnPrepare, "on_prepare", True)(func)


class OnStart(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_start", func)
        return func


def on_start(func):
    return get_decorator(OnStart, "on_start", True)(func)


class OnStop(DecoratorBase):
    def __init__(self, decorator_name, *args, **kwargs):
        assert isinstance(kwargs.get("immediate", False), bool), (
            f"{decorator_name} parameter 'immediate' should be True or "
            f"False, not {kwargs['immediate']}"
        )
        self.immediate = kwargs.get("immediate", False)
        super().__init__(decorator_name, *args, **kwargs)

    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        if self.immediate:
            CallbackBase.register_callback("on_stop(immediate=True)", func)
        else:
            CallbackBase.register_callback("on_stop", func)
        return func


def on_stop(*func, immediate=False):
    return get_decorator(OnStop, "on_stop", False)(
        *func, **{"immediate": immediate}
    )


class OnExit(DecoratorBase):
    def __init__(self, decorator_name, *args, **kwargs):
        assert isinstance(kwargs.get("immediate", False), bool), (
            f"{decorator_name} parameter 'immediate' should be True or "
            f"False, not {kwargs['immediate']}"
        )
        self.immediate = kwargs.get("immediate", False)
        super().__init__(decorator_name, *args, **kwargs)

    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        if self.immediate:
            CallbackBase.register_callback("on_exit(immediate=True)", func)
        else:
            CallbackBase.register_callback("on_exit", func)
        return func


def on_exit(*func, immediate=False):
    return get_decorator(OnExit, "on_exit", False)(
        *func, **{"immediate": immediate}
    )


class OnTime(DecoratorBase):
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


def on_time(func):
    return get_decorator(OnTime, "on_time", False)(func)


class OnRepeat(DecoratorBase):
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


def on_repeat(func):
    return get_decorator(OnRepeat, "on_repeat", True)(func)
