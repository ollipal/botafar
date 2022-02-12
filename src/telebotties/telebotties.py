import asyncio
import concurrent.futures
import sys
import time
import traceback

from .constants import (
    LISTEN_KEYBOARD_MESSAGE,
    LISTEN_MESSAGE,
    LISTEN_WEB_MESSAGE,
)
from .inputs import Event, InputBase
from .listeners import (
    _listen_keyboard_wrapper,
    _start_listening_enter,
    _stop_listening_enter,
)

_executor = concurrent.futures.ThreadPoolExecutor()
_loop = asyncio.get_event_loop()
_futures = set()


# Fix Python3.6 asyncio.run()
if sys.version_info.major == 3 and sys.version_info.minor == 6:
    from misc import run36

    asyncio.run = run36


def _check_future_result(future):
    try:
        result = (
            future.result()
        )  # TODO do something with event handler results?
    except asyncio.CancelledError:
        pass
    except Exception as e:
        traceback.print_exc()
        print("EXCEPTION")  # TODO stop execution somehow?
    finally:
        _futures.remove(future)


def _process_input(key, sender, origin, name):
    event_key = (key, sender, origin)
    if event_key not in InputBase._event_callbacks:
        return

    event = Event(name, True, sender, origin, -1)
    callbacks = InputBase._event_callbacks[
        event_key
    ]._get_callbacks_with_parameters(key, event)

    if callbacks is None:
        return

    # Set callbacks to execute soon (non-blocking)
    # TODO check sshkeyboard for more up to date handling?
    for callback, param in callbacks:
        # TODO use param
        if asyncio.iscoroutinefunction(callback):
            future = asyncio.run_coroutine_threadsafe(callback(), _loop)
        else:
            future = _executor.submit(callback)  # , param)
        _futures.add(future)
        _executor.submit(_check_future_result, future)


async def _main():
    listen_keyboard_non_blocking = _listen_keyboard_wrapper(_process_input)
    listener = listen_keyboard_non_blocking()

    try:
        while listener.running:
            await asyncio.sleep(0.1)
    finally:
        listener.stop()
        print()


def listen():
    print(LISTEN_MESSAGE, end="")
    enter_event = _start_listening_enter()
    for _ in range(50):
        time.sleep(0.1)
        if enter_event.is_set():
            break

    if enter_event.is_set():
        print(LISTEN_KEYBOARD_MESSAGE)
        asyncio.run(_main())
    else:
        _stop_listening_enter()
        print(LISTEN_WEB_MESSAGE)
