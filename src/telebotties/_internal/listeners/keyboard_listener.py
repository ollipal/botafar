import asyncio

from ..constants import (
    KEYS,
    LISTEN_LOCAL_KEYBOARD_MESSAGE,
    LISTEN_REMOTE_KEYBOARD_MESSAGE,
)
from ..events import Event, SystemEvent
from ..log_formatter import get_logger
from ..string_utils import control_list_string, error_to_string

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
    CTRLS = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
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
        # For ctrl + c detection, when suppressed
        self._ctrl_pressed = False
        self._c_pressed = False

    async def run_until_finished(self, control_datas, local):  # noqa: C901
        if self.running:
            logger.debug("KeyboardListener was already running")
            return

        self._running = True
        self._stop_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()

        def on_press(key):
            try:
                if key in CTRLS:
                    self._ctrl_pressed = True
                    return  # Cannot trigger anything else
                elif hasattr(key, "char") and key.char.upper() == "C":
                    self._c_pressed = True

                if key == keyboard.Key.esc or (
                    self._ctrl_pressed and self._c_pressed
                ):
                    if not self._suppress_keys and not self.prints_removed:
                        print()  # makes new line for easier reading (linux)
                    self.stop()
                    return False

                if key == keyboard.Key.backspace:
                    event = SystemEvent("player_disconnect", "keyboard")
                    self._process_event(event)
                    return

                key = _format_key(key)
                if key is not None and not is_pressed[key]:
                    event = Event("on_press", "player", key)
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
                if key in CTRLS:
                    self._ctrl_pressed = False
                    return  # Cannot trigger anything else
                elif hasattr(key, "char") and key.char.upper() == "C":
                    self._c_pressed = False

                key = _format_key(key)
                if key is not None and is_pressed[key]:
                    event = Event("on_release", "player", key)
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
            print(control_list_string(control_datas))

        event = SystemEvent("host_connect", "host")
        self._process_event(event)
        if local:
            event = SystemEvent("player_connect", "player")
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
