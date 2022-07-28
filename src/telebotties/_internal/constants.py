from .string_utils import bold, dim, key, underlined

KEYS = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "SPACE",
    "UP",
    "LEFT",
    "DOWN",
    "RIGHT",
}

SENDERS = {"player", "host"}
ORIGINS = {"keyboard", "screen"}

INPUT_EVENT = "INPUT_EVENT"
SYSTEM_EVENT = "SYSTEM_EVENT"

LISTEN_LOCAL_KEYBOARD_MESSAGE = f"""

{bold("Listening to local keyboard events")} {dim("(web connection listening stopped)")}
Press {key("Esc")} to exit, {key("Backspace")} to reconnect player.

{underlined("Custom controls")}:"""

LISTEN_REMOTE_KEYBOARD_MESSAGE = f"""
{bold("A remote keyboard connected successfully")}
Press {key("Esc")} to exit, {key("Backspace")} to reconnect player.

{underlined("Custom controls")}:"""

LISTEN_WEB_MESSAGE_PYNPUT = (
    f"\n\n\n{bold('Connected')} {dim('(will not listen to local keyboard events)')}\n"
    f"Press {key('Ctrl')} + {key('C')} to exit.\n"
)

LISTEN_WEB_MESSAGE_NO_PYNPUT = (
    f"\n\n\n{bold('Connected')}\n"
    f"Press {key('Ctrl')} + {key('C')} to exit.\n"
)

SIGINT_MESSAGE = (
    f"\n\n{key('Ctrl')} + {key('C')} received, "
    f"shutting down gracefully... {dim('(Press again to exit immediately)')}"
)

# TODO a separate message on when pynput cannot be initialized,
# and should be connected from remotely
