from .misc import _bold, _dim, _key

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

LISTEN_MESSAGE = f"""Listening to web connections at 192.168.1.123:1996

Go to {_bold("http://localhost:3000/new?address=192-168-1-123-1996")} to connect
  or
Press {_key("ENTER")} to start listening to local keyboard events: """

LISTEN_KEYBOARD_MESSAGE = f"""

{_bold("Listening to local keyboard events")}, web connection listening stopped.
- stop listening and exit: {_key('Esc')}
- send keyboard events as player: {_key("1")} {_dim("(default)")}
- send keyboard events as host: {_key("0")}
- simulate player getting disconnected: {_key("Enter")}
"""

LISTEN_WEB_MESSAGE = f"Connected to web, will not listen to local keyboard events.\n\nPress {_key('Ctrl')} + {_key('C')} to exit.\n"

# TODO a separate message on when pynput cannot be initialized, and should be connected from remotely
