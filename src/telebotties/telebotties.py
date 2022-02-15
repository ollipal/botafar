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
_loop = None  # Will be set in _main
_should_run = True
_futures = set()


# Fix Python3.6 asyncio.run()
if sys.version_info.major == 3 and sys.version_info.minor == 6:
    from misc import run36

    asyncio.run = run36


def _done(future):
    if not future.cancelled() and future.exception() is not None:
        ex = future.exception()
        traceback.print_exception(type(ex), ex, ex.__traceback__)
        global _should_run
        _should_run = False
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
    for callback, takes_event in callbacks:
        # TODO use param
        if asyncio.iscoroutinefunction(callback):
            if takes_event:
                future = _loop.create_task(callback(event))
            else:
                future = _loop.create_task(callback())
        else:
            if takes_event:
                future = _executor.submit(callback, event)
            else:
                future = _executor.submit(callback)
        _futures.add(future)
        future.add_done_callback(_done)


async def _main():
    global _loop
    _loop = asyncio.get_running_loop()

    listen_keyboard_non_blocking = _listen_keyboard_wrapper(_process_input)
    listener = listen_keyboard_non_blocking()

    try:
        while _should_run and listener.running:
            await asyncio.sleep(0.1)
    finally:
        listener.wait()
        listener.stop()
        print()
    # TODO cancel futures?


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
