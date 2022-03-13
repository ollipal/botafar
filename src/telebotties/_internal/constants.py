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

LISTEN_MESSAGE = f"""Listening to web connections at 192.168.1.123:1996

Go to {bold("http://localhost:3000/new?address=192-168-1-123-1996")} to connect
  or
Press {key("ENTER")} to start listening to local keyboard events: """

LISTEN_KEYBOARD_MESSAGE = f"""

{bold("Listening to local keyboard events")} {dim("(web connection listening stopped)")}
Press {key("Esc")} to exit, {key("Enter")} to reconnect player.

{underlined("Custom inputs")}:"""

LISTEN_WEB_MESSAGE = (
    f"\n\n\n{bold('Connected to a remote keyboard')} {dim('(will not listen to local keyboard events)')}\n"
    f"Press {key('Ctrl')} + {key('C')} to exit.\n"
)

SIGINT_MESSAGE = (
    f"\n\n{key('Ctrl')} + {key('C')} received, "
    f"shutting down gracefully... {dim('(Press again to exit immediately)')}"
)

# TODO a separate message on when pynput cannot be initialized,
# and should be connected from remotely
