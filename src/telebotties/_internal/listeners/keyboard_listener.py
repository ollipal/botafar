import asyncio

from ..constants import KEYS, LISTEN_KEYBOARD_MESSAGE
from ..events import Event
from ..log_formatter import get_logger

logger = get_logger()

try:
    from pynput import keyboard

    PYNPUT_KEY_TO_KEY = {
        keyboard.Key.space: "SPACE",
        keyboard.Key.up: "UP",
        keyboard.Key.left: "LEFT",
        keyboard.Key.down: "DOWN",
        keyboard.Key.right: "RIGHT",
    }
    pynput_supported = True
except ImportError:
    pynput_supported = False


def _format_key(key):
    if key in PYNPUT_KEY_TO_KEY.keys():
        return PYNPUT_KEY_TO_KEY[key]

    try:
        char = key.char.upper()
    except AttributeError:
        return None

    if char in KEYS:
        return char

    return None


class KeyboardListener:
    def __init__(self, event_handler, suppress_keys):
        self._event_handler = event_handler
        self._suppress_keys = suppress_keys
        self._running = False
        self._event = None

    async def run_until_finished(self):
        if self.running:
            logger.debug("KeyboardListener was already running")
            return

        self._running = True
        self._event = asyncio.Event()
        self._loop = asyncio.get_running_loop()

        def on_press(key):
            key = _format_key(key)
            if key is not None:
                event = Event("press", "host", "keyboard", key)
                self._event_handler(event)

        def on_release(key):
            if key == keyboard.Key.esc:
                self.stop()
                return False

            key = _format_key(key)
            if key is not None:
                event = Event("release", "host", "keyboard", key)
                self._event_handler(event)

        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release,
            suppress=self._suppress_keys,
        )
        listener.start()
        listener.wait()

        print(LISTEN_KEYBOARD_MESSAGE)
        try:
            await self._event.wait()
        finally:
            print()

    def stop(self):
        if not self.running:
            logger.debug("KeyboardListener was not running")
            return

        self._running = False
        self._loop.call_soon_threadsafe(self._event.set)

    @property
    def running(self):
        return self._running
