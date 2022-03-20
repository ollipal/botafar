import asyncio

from ..constants import (
    KEYS,
    LISTEN_LOCAL_KEYBOARD_MESSAGE,
    LISTEN_REMOTE_KEYBOARD_MESSAGE,
)
from ..events import Event, SystemEvent
from ..log_formatter import get_logger
from ..string_utils import error_to_string, input_list_string

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
except Exception:
    logger.debug("pynput not supported")
    pynput_supported = False

is_pressed = {key: False for key in KEYS}


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
    def __init__(self, process_event, suppress_keys, prints_removed):
        self._process_event = process_event
        self._suppress_keys = suppress_keys
        self.prints_removed = prints_removed
        self._running = False
        self._stop_event = None

    async def run_until_finished(self, input_datas, local):
        if self.running:
            logger.debug("KeyboardListener was already running")
            return

        self._running = True
        self._stop_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()

        def on_press(key):
            try:
                key = _format_key(key)
                if key is not None and not is_pressed[key]:
                    event = Event("press", "player", "keyboard", key)
                    self._process_event(event)
                    is_pressed[key] = True
            except Exception as e:
                logger.error(
                    f"Unexpected internal error:\n{error_to_string(e)}"
                )
                self.stop()
                return False

        def on_release(key):
            try:
                if key == keyboard.Key.esc:
                    if not self._suppress_keys and not self.prints_removed:
                        print()  # makes new line for easier reading (linux)
                    event = SystemEvent("client_disconnect", "keyboard")
                    self._process_event(event)
                    self.stop()
                    return False

                key = _format_key(key)
                if key is not None and is_pressed[key]:
                    event = Event("release", "player", "keyboard", key)
                    self._process_event(event)
                    is_pressed[key] = False
            except Exception as e:
                logger.error(
                    f"Unexpected internal error:\n{error_to_string(e)}"
                )
                self.stop()
                return False

        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release,
            suppress=self._suppress_keys,
        )
        listener.start()
        listener.wait()

        if not self.prints_removed:
            if local:
                print(LISTEN_LOCAL_KEYBOARD_MESSAGE)
            else:
                print(LISTEN_REMOTE_KEYBOARD_MESSAGE)
            print(input_list_string(input_datas))

        event = SystemEvent("client_connect", "keyboard")
        self._process_event(event)
        if local:
            event = SystemEvent("player_connect", "keyboard")
            self._process_event(event)
        await self._stop_event.wait()

    def stop(self):
        if not self.running:
            logger.debug("KeyboardListener was not running")
            return

        self._running = False
        self._loop.call_soon_threadsafe(self._stop_event.set)

    @property
    def running(self):
        return self._running
