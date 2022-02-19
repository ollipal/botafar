import asyncio
import traceback
import signal

from .listeners import listen_keyboard_wrapper
from .log_formatter import get_logger
from .websocket import Client
from .constants import (
    LISTEN_KEYBOARD_MESSAGE,
    SIGINT_MESSAGE,
)

logger = get_logger()

# Will be set in _main()
client = None
loop = None
listener = None


async def _stop_listener():
    global listener
    listener.wait()
    listener.stop()


def _done(future):
    if not future.cancelled() and future.exception() is not None:
        global listener
        if listener.running:
            ex = future.exception()
            exception_string = "".join(
                traceback.format_exception(type(ex), ex, ex.__traceback__)
            )
            logger.error(exception_string)
            loop.create_task(_stop_listener())

    if future.result() is False:  # Send failed
        logger.info("disconnected")
        loop.create_task(_stop_listener())


def _process_input(key, sender, origin, name):
    future = loop.create_task(client.send(key, sender, origin, name))
    future.add_done_callback(_done)  # TODO raising error on send does not


async def _main():
    global loop
    global client
    global listener
    loop = asyncio.get_running_loop()
    client = Client(8080)

    try:
        await client.connect()
    except ConnectionRefusedError:
        print(
            "Connection refused to 127.0.0.1:8080, "
            "wrong address or bot not running?"
        )
        return

    # Check even first send, it does not raise errors
    # (they do not seem to work as expected)
    res = await client.send("A", "player", "keyboard", "connect")
    if not res:
        await client.stop()
        return
    
    print(LISTEN_KEYBOARD_MESSAGE)

    listen_keyboard_non_blocking = listen_keyboard_wrapper(_process_input)
    listener = listen_keyboard_non_blocking()

    try:
        while listener.running:
            await asyncio.sleep(0.1)
    finally:
        await client.stop()
        print()
    
    await asyncio.sleep(2)


def _cli():
    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def signal_handler(_signal, frame):
        signal.signal(signal.SIGINT, original_sigint_handler)  # Reset
        print(SIGINT_MESSAGE)
        asyncio.run_coroutine_threadsafe(_stop_listener(), loop)

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.run(_main())
