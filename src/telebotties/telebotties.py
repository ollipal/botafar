from listen_keyboard import _listen_keyboard_wrapper


def _process_input(key, sender, origin):
    print(key)


listen_keyboard = _listen_keyboard_wrapper(_process_input)
