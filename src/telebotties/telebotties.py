import asyncio
import sys

from _asyncio_run_backport_36 import run36
from listen_keyboard import _listen_keyboard_wrapper


def _is_python_36():
    return sys.version_info.major == 3 and sys.version_info.minor == 6


def _process_input(key, sender, origin):
    print(key)


async def _main():
    listen_keyboard_non_blocking = _listen_keyboard_wrapper(_process_input)
    listener = listen_keyboard_non_blocking()

    try:
        while listener.running:
            await asyncio.sleep(0.1)
    finally:
        listener.stop()


def listen_keyboard():
    if _is_python_36():
        run36(_main())
    else:
        asyncio.run(_main())
