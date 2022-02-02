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
    def _listen_keyboard():
        def _on_press(key):
            process_input(_format_key(key), "host", "keyboard")

        def _on_release(key):
            if key == keyboard.Key.esc:
                return False

            process_input(_format_key(key), "host", "keyboard")

        with keyboard.Listener(
            on_press=_on_press, on_release=_on_release
        ) as listener:
            listener.join()

    return _listen_keyboard


if __name__ == "__main__":

    def _dummy_process_input(key, sender, origin):
        if key is not None:
            print(key)

    listen_keyboard = _listen_keyboard_wrapper(_dummy_process_input)
    listen_keyboard()
