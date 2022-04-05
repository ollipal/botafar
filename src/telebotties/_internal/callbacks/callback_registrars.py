import asyncio
import copy

from ..log_formatter import get_logger
from ..states import sleep as sleep_
from ..states import sleep_async
from . import CallbackBase

logger = get_logger()


def on_init(function):
    CallbackBase.register_callback("on_init", function)
    return function


def on_exit(*args, immediate=False):
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


def on_time(*time):
    def wrapper_async(t, function):
        async def _wrapper_async():
            await sleep_async(t)
            if CallbackBase._takes_time(function):
                await function(t)
            else:
                await function()

        return copy.deepcopy(_wrapper_async)

    def wrapper_sync(t, function):
        def _wrapper_sync():
            sleep_(t)
            if CallbackBase._takes_time(function):
                function(t)
            else:
                function()

        return _wrapper_sync

    def _on_time(function):
        # Weird errors with _wrapper_async with same time always...
        if asyncio.iscoroutinefunction(function) and len(time) > 1:
            raise RuntimeError(
                "Asyncronous on_time currently supports only one time"
            )

        for t in time:
            assert isinstance(
                t, (int, float)
            ), "Times must be of type int or float"
            assert t >= 0, "Times must be positive"

            if asyncio.iscoroutinefunction(function):
                CallbackBase.register_callback(
                    "on_time", copy.deepcopy(wrapper_async(t, function))
                )
            else:
                CallbackBase.register_callback(
                    "on_time", copy.deepcopy(wrapper_sync(t, function))
                )

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
