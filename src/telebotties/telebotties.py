import asyncio
import concurrent.futures
import traceback

from .constants import (
    LISTEN_KEYBOARD_MESSAGE,
    LISTEN_MESSAGE,
    LISTEN_WEB_MESSAGE,
    SIGINT_MESSAGE,
)
from .inputs import Event, InputBase
from .listeners import (
    _listen_keyboard_wrapper,
    _start_listening_enter,
    _stop_listening_enter,
)
from .log_formatter import get_logger, setup_logging
from .websocket import Server

setup_logging("DEBUG")
logger = get_logger()

_executor = concurrent.futures.ThreadPoolExecutor()
_loop = None  # Will be set in _main
_listener = None
_futures = set()
_server = None
_connected = False


async def _stop_listener():
    global _listener
    if _listener is not None:
        _listener.wait()
        _listener.stop()
    else:
        logger.debug("listener was None")


def _done(future):
    _futures.remove(future)
    if not future.cancelled() and future.exception() is not None:
        global _listener
        if _listener.running:
            ex = future.exception()
            exception_string = "".join(
                traceback.format_exception(type(ex), ex, ex.__traceback__)
            )
            logger.error(exception_string)
            asyncio.run_coroutine_threadsafe(_stop_listener(), _loop)


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
                future = asyncio.run_coroutine_threadsafe(
                    callback(event), _loop
                )
            else:
                future = asyncio.run_coroutine_threadsafe(callback(), _loop)
        else:
            if takes_event:
                future = _executor.submit(callback, event)
            else:
                future = _executor.submit(callback)
        _futures.add(future)
        future.add_done_callback(_done)


async def _main():
    global _loop
    global _server
    _loop = asyncio.get_running_loop()

    print(LISTEN_MESSAGE, end="")

    def event_handler(event):
        if "connect" in event:
            global _connected
            _stop_listening_enter()
            print(LISTEN_WEB_MESSAGE)
            _connected = True
        print(f"event={event}")

    _server = Server(event_handler)

    enter_event = _start_listening_enter()

    async def wait_enter():
        global _connected
        while not _connected:
            if enter_event.is_set():
                _server.stop()
                break
            await asyncio.sleep(0.1)

    await asyncio.gather(
        _server.serve(8080),
        wait_enter(),
    )

    if not _connected:
        print(LISTEN_KEYBOARD_MESSAGE)

        global _listener
        listen_keyboard_non_blocking = _listen_keyboard_wrapper(_process_input)
        _listener = listen_keyboard_non_blocking()

        try:
            # asyncio.Event() would be cleaner if can get to work
            while _listener.running:
                await asyncio.sleep(0.1)
        finally:
            print()

    await asyncio.sleep(2)

    # TODO wait futures?


def listen():
    import signal

    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def signal_handler(_signal, frame):
        signal.signal(signal.SIGINT, original_sigint_handler)  # Reset
        print(SIGINT_MESSAGE)
        global server
        _server.stop()
        _stop_listening_enter() # Not sure if this ok
        global _connected
        _connected = True # TODO better way
        asyncio.run_coroutine_threadsafe(_stop_listener(), _loop)

    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(_main())
