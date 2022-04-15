import asyncio

from ..log_formatter import get_logger
from ..states import sleep as sleep_
from ..states import sleep_async, state_machine
from ..states import time as time_
from . import CallbackBase

logger = get_logger()


# def on_init(function):
#    CallbackBase.register_callback("on_init", function)
#    return function


def on_exit(*args, immediate=False):
    # NOTE: sleep and sleep_async do not work when immediate=True
    def _on_exit(function):
        if immediate:
            CallbackBase.register_callback("on_exit(immediate=True)", function)
        else:
            CallbackBase.register_callback("on_exit", function)
        return function

    if len(args) == 1 and callable(args[0]):  # Regular
        return _on_exit(args[0])
    elif len(args) == 0:  # With empty parenthesis
        return _on_exit
    elif len(args) == 1 and isinstance(
        args[0], bool
    ):  # No keyword or with keyword
        raise RuntimeError(
            f"'immediate' requires a keyword, use on_exit(immediate={args[0]})"
        )
    else:
        raise RuntimeError("Unknown parameters for on_exit")  # TODO url


def on_prepare(function):
    CallbackBase.register_callback("on_prepare", function)
    return function


def on_start(*args, before_controls=False):
    def _on_start(function):
        if before_controls:
            CallbackBase.register_callback(
                "on_start(before_controls=True)", function
            )
        else:
            CallbackBase.register_callback("on_start", function)
        return function

    if len(args) == 1 and callable(args[0]):  # Regular
        return _on_start(args[0])
    elif len(args) == 0:  # With empty parenthesis or with keyword
        return _on_start
    elif len(args) == 1 and isinstance(args[0], bool):  # No keyword
        raise RuntimeError(
            "'before_controls' requires a keyword, "
            f"use on_start(before_controls={args[0]})"
        )
    else:
        raise RuntimeError("Unknown parameters for on_start")  # TODO url


def on_stop(*args, immediate=False):
    # NOTE: sleep and sleep_async do not work when immediate=True
    def _on_stop(function):
        if immediate:
            CallbackBase.register_callback("on_stop(immediate=True)", function)
        else:
            CallbackBase.register_callback("on_stop", function)
        return function

    if len(args) == 1 and callable(args[0]):  # Regular
        return _on_stop(args[0])
    elif len(args) == 0:  # With empty parenthesis or with keyword
        return _on_stop
    elif len(args) == 1 and isinstance(args[0], bool):  # No keyword
        raise RuntimeError(
            f"'immediate' requires a keyword, use on_stop(immediate={args[0]})"
        )
    else:  # With keyword
        raise RuntimeError("Unknown parameters for on_stop")  # TODO url


# NOTE: does not allow at the same time,
# will fire too late if takes too much time
def on_time(*time):
    def _on_time(function):
        sorted_times = sorted(time)

        if asyncio.iscoroutinefunction(function):
            """NOT WORKING!!!
            import copy
                async def wrapper():
                    for t in sorted_times:
                        if CallbackBase._takes_time(function):
                            async def func():
                                await function(copy.deepcopy(t))
                        else:
                            func = function

                        now = time_()
                        if now == -1:
                            logger.warning("on_time time is -1???")
                            break

                        sleep_(max(0, t - now))
                        state_machine.execute_on_time_from_outside(copy.deepcopy(func))
                        print("Here")
            """

            async def wrapper():
                for t in sorted_times:
                    now = time_()
                    if now == -1:
                        logger.warning("on_time time is -1???")
                        break

                    sleep_time = max(0, t - now)
                    await sleep_async(sleep_time)
                    if sleep_time == 0:
                        logger.warning(
                            f"on_time({t}) callback start was delayed, "
                            "previous callback took too much time "
                            "(this is a limitation only with async methods)"
                        )
                    if CallbackBase._takes_time(function):
                        await function(t)
                    else:
                        await function()

        else:

            def wrapper():
                for t in sorted_times:
                    if CallbackBase._takes_time(function):

                        def func():
                            function(t)

                    else:
                        func = function

                    now = time_()
                    if now == -1:
                        logger.warning("on_time time is -1???")
                        break

                    sleep_(max(0, t - now))
                    state_machine.execute_on_time_from_outside(func)

        CallbackBase.register_callback("on_time", wrapper)
        return function

    if len(time) == 1 and callable(time[0]):  # Regular
        raise RuntimeError("Define time to trigger: for example on_time(5)")
    elif len(time) == 0:  # With empty parenthesis
        raise RuntimeError("Define time to trigger: for example on_time(5)")
    else:  # Correct
        return _on_time


def on_repeat(*args, sleep=0.1):
    assert isinstance(
        sleep, (int, float)
    ), "Sleep must be of type int or float"
    assert sleep >= 0, "Sleep must be positive"

    def _on_repeat(function):
        if asyncio.iscoroutinefunction(function):

            async def wrapper():
                while True:
                    await function()
                    await sleep_async(sleep)

        else:

            def wrapper():
                while True:
                    function()
                    sleep_(sleep)

        CallbackBase.register_callback("on_repeat", wrapper)
        return function

    if len(args) == 1 and callable(args[0]):  # Regular
        return _on_repeat(args[0])
    elif len(args) == 0:  # With empty parenthesis or with keyword
        return _on_repeat
    elif len(args) == 1 and isinstance(args[0], (int, float)):  # No keyword
        raise RuntimeError(
            f"'sleep' requires a keyword, use on_repeat(sleep={args[0]})"
        )
    else:  # With keyword
        raise RuntimeError("Unknown parameters for on_repeat")  # TODO url
