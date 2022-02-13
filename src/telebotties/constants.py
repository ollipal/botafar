from .misc import _dim, _bold, _key

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

LISTEN_MESSAGE = f"""
Listening to web connections at:
- 127.0.0.1:1996\t{_dim("(this device)")}
- 192.168.1.123:1996\t{_dim("(this network)")}

Go to {_bold("http://localhost:3000/new")} to connect
  or
Press {_key("ENTER")} to start listening to local keyboard events: """

LISTEN_KEYBOARD_MESSAGE = f"""

{_bold("Listening to local keyboard events")} {_dim("(web connection listening stopped)")}
- stop listening and exit: {_key("ESC")}
- send keyboard events as player: {_key("1")} {_dim("(default)")}
- send keyboard events as host: {_key("0")}
- simulate player getting disconnected: {_key("ENTER")}
"""

LISTEN_WEB_MESSAGE = (
    "Connected to web, will not listen to local keyboard events.\n"
)
