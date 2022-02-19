import asyncio

from ..constants import KEYS, LISTEN_KEYBOARD_MESSAGE

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
        assert not self.running
        self._running = True
        self._event = asyncio.Event()
        self._loop = asyncio.get_running_loop()

        def on_press(key):
            key = _format_key(key)
            if key is not None:
                self._event_handler(key, "host", "keyboard", "press")

        def on_release(key):
            if key == keyboard.Key.esc:
                self.stop()
                return False

            key = _format_key(key)
            if key is not None:
                self._event_handler(key, "host", "keyboard", "release")

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
        assert self.running
        self._running = False
        self._loop.call_soon_threadsafe(self._event.set)

    @property
    def running(self):
        return self._running
