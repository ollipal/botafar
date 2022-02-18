import asyncio
import traceback

from .listeners import _listen_keyboard_wrapper
from .log_formatter import get_logger
from .websocket import Client

logger = get_logger()

# Will be set in _main()
_client = None
_loop = None
_listener = None


async def _stop_listener():
    global _listener
    _listener.wait()
    _listener.stop()


def _done(future):
    if not future.cancelled() and future.exception() is not None:
        global _listener
        if _listener.running:
            ex = future.exception()
            exception_string = "".join(
                traceback.format_exception(type(ex), ex, ex.__traceback__)
            )
            logger.error(exception_string)
            _loop.create_task(_stop_listener())

    if future.result() is False:  # Send failed
        logger.info("disconnected")
        _loop.create_task(_stop_listener())


def _process_input(key, sender, origin, name):
    future = _loop.create_task(_client.send(key, sender, origin, name))
    future.add_done_callback(_done)  # TODO raising error on send does not


async def _main():
    global _loop
    global _client
    global _listener
    _loop = asyncio.get_running_loop()
    _client = Client(8080)

    try:
        await _client.connect()
    except ConnectionRefusedError:
        print(
            "Connection refused to 127.0.0.1:8080, "
            "wrong address or bot not running?"
        )
        return

    # Check even first send, it does not raise errors
    # (they do not seem to work as expected)
    res = await _client.send("A", "player", "keyboard", "connect")
    if not res:
        await _client.stop()
        return

    listen_keyboard_non_blocking = _listen_keyboard_wrapper(_process_input)
    _listener = listen_keyboard_non_blocking()

    try:
        while _listener.running:
            await asyncio.sleep(0.1)
    finally:
        await _client.stop()
        print()


def _cli():
    asyncio.run(_main())
