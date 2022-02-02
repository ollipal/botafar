from constants import KEYS
from pynput import keyboard

PYNPUT_KEY_TO_KEY = {
    keyboard.Key.space: "SPACE",
    keyboard.Key.up: "UP",
    keyboard.Key.left: "LEFT",
    keyboard.Key.down: "DOWN",
    keyboard.Key.right: "RIGHT",
}


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


def _listen_keyboard_wrapper(process_input):
    def listen_keyboard_non_blocking():
        def on_press(key):
            process_input(_format_key(key), "host", "keyboard")

        def on_release(key):
            if key == keyboard.Key.esc:
                return False

            process_input(_format_key(key), "host", "keyboard")

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        return listener

    return listen_keyboard_non_blocking


if __name__ == "__main__":
    import time

    def dummy_process_input(key, sender, origin):
        if key is not None:
            print(key)

    listen_keyboard_non_blocking = _listen_keyboard_wrapper(
        dummy_process_input
    )
    listener = listen_keyboard_non_blocking()

    try:
        while listener.running:
            time.sleep(0.1)
    finally:
        listener.stop()
