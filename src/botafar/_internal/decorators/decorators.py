import asyncio

from ..callbacks import CallbackBase
from ..function_utils import (
    get_function_title,
    get_required_params,
    takes_parameter,
)
from ..log_formatter import get_logger
from ..states import sleep, sleep_async, state_machine, time
from .decorator_base import DecoratorBase, get_decorator

logger = get_logger()


class OnInit(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func


def on_init(func):
    title = get_function_title(func)
    return get_decorator(OnInit, title, "on_init", True)(func)


class OnPrepare(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        CallbackBase.register_callback("on_prepare", func)
        return func


def on_prepare(func):
    title = get_function_title(func)
    return get_decorator(OnPrepare, title, "on_prepare", True)(func)


class OnStart(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        CallbackBase.register_callback("on_start", func)
        return func


def on_start(func):
    title = get_function_title(func)
    return get_decorator(OnStart, title, "on_start", True)(func)


class OnStop(DecoratorBase):
    def __init__(self, title, decorator_name, *args, **kwargs):
        assert isinstance(kwargs.get("immediate", False), bool), (
            f"{decorator_name} parameter 'immediate' should be True or "
            f"False, not {kwargs['immediate']}"
        )
        self.immediate = kwargs.get("immediate", False)
        super().__init__(title, decorator_name, *args, **kwargs)

    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        if self.immediate:
            CallbackBase.register_callback("on_stop(immediate=True)", func)
        else:
            CallbackBase.register_callback("on_stop", func)
        return func


def on_stop(*func, immediate=False):
    if len(func) >= 1 and (
        isinstance(func[0], (classmethod, staticmethod)) or callable(func[0])
    ):
        title = get_function_title(func[0])
    else:
        title = "TITLE"

    return get_decorator(OnStop, title, "on_stop", False)(
        *func, **{"immediate": immediate}
    )


class OnExit(DecoratorBase):
    def __init__(self, title, decorator_name, *args, **kwargs):
        assert isinstance(kwargs.get("immediate", False), bool), (
            f"{decorator_name} parameter 'immediate' should be True or "
            f"False, not {kwargs['immediate']}"
        )
        self.immediate = kwargs.get("immediate", False)
        super().__init__(title, decorator_name, *args, **kwargs)

    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        if self.immediate:
            CallbackBase.register_callback("on_exit(immediate=True)", func)
        else:
            CallbackBase.register_callback("on_exit", func)
        return func


def on_exit(*func, immediate=False):
    if len(func) >= 1 and (
        isinstance(func[0], (classmethod, staticmethod)) or callable(func[0])
    ):
        title = get_function_title(func[0])
    else:
        title = "TITLE"

    return get_decorator(OnExit, title, "on_exit", False)(
        *func, **{"immediate": immediate}
    )


class OnTime(DecoratorBase):
    def __init__(self, title, decorator_name, *args, **kwargs):
        assert len(args) > 1, (
            f"{decorator_name} takes one or more times as parameter"
            f"for example '@botafar.{decorator_name}(5)' "
            f"or '@botafar.{decorator_name}(1, 2, 3)' "
        )
        self.times = args[1:]

        assert all(isinstance(time, (int, float)) for time in self.times), (
            f"{decorator_name} all times should be numeric (int or float), "
            f"current times: {self.times}"
        )
        assert self.times == tuple(sorted(self.times)), (
            f"{decorator_name} times should be sorted from smallest to "
            f"largest, current times: {self.times}"
        )

        super().__init__(title, decorator_name, args[0], **kwargs)

    def verify_params_and_set_flags(self, params):  # noqa: N805
        if takes_parameter(params, "time", error_name=self.decorator_name):
            self.takes_time = True
        else:
            self.takes_time = False

    def wrap(self, func):
        def get_wrapper(args, t):
            if asyncio.iscoroutinefunction(func):
                if self.takes_time:

                    async def wrapper():
                        return await func(*args, t)

                else:

                    async def wrapper():
                        return await func(*args)

            else:
                if self.takes_time:

                    def wrapper():
                        return func(*args, t)

                else:

                    def wrapper():
                        return func(*args)

            return wrapper

        async def outer_wrapper(*args):
            for t in self.times:
                now = time()
                if now == -1:
                    logger.warning("on_time time is -1???")
                    break

                await sleep_async(max(0, t - now))
                state_machine.execute_on_time_from_outside(
                    get_wrapper(args, t)
                )

        CallbackBase.register_callback("on_time", outer_wrapper)
        return func


def on_time(func, *time):
    if isinstance(func, (classmethod, staticmethod)) or callable(func):
        title = get_function_title(func)
    else:
        title = "TITLE"

    return get_decorator(OnTime, title, "on_time", False)(func, *time)


class OnRepeat(DecoratorBase):
    def __init__(self, title, decorator_name, *args, **kwargs):
        assert not (len(args) == 2 and isinstance(args[1], (int, float))), (
            f"{decorator_name} parameter 'sleep' should be passed "
            f"with a keyword: '@botafar.{decorator_name}(sleep={args[1]})'"
        )
        assert "sleep" in kwargs
        self.sleep = kwargs["sleep"]
        assert isinstance(self.sleep, (int, float)), (
            f"{decorator_name} parameter 'sleep' should be numeric "
            f"(int or float), not '{self.sleep}'"
        )
        assert (
            self.sleep >= 0
        ), f"{decorator_name} parameter 'sleep' cannot be negative"
        self.immediate = kwargs.get("sleep", False)
        super().__init__(title, decorator_name, *args, **kwargs)

    def verify_params_and_set_flags(self, params):
        required = get_required_params(params)
        assert len(required) == 0, (
            f"{self.decorator_name} callback parameters need to be optional, "
            f"currently required parameters {required} need to be made "
            "optional or removed"
        )

    def wrap(self, func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args):
                while True:
                    await func(*args)
                    await sleep_async(self.sleep)

        else:

            def wrapper(*args):
                while True:
                    func(*args)
                    sleep(self.sleep)

        CallbackBase.register_callback("on_repeat", wrapper)
        return func


def on_repeat(*func, sleep=0.1):
    if len(func) >= 1 and (
        isinstance(func[0], (classmethod, staticmethod)) or callable(func[0])
    ):
        title = get_function_title(func[0])
    else:
        title = "TITLE"

    return get_decorator(OnRepeat, title, "on_repeat", False)(
        *func, **{"sleep": sleep}
    )
