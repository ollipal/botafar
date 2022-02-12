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

LISTEN_MESSAGE = """
Listening to web connections at:
- \033[1m127.0.0.1:1996\033[0m\t\033[2m(this device)\033[0m
- \033[1m192.168.1.123:1996\033[0m\t\033[2m(this network)\033[0m

Go to \033[1mhttp://localhost:3000/new\033[0m to connect
  or
Press \033[1;30;107m ENTER \033[0m to start listening to local keyboard events: """

LISTEN_KEYBOARD_MESSAGE = """
\033[1mListening to local keyboard events\033[0m \033[2m(web connection listening stopped)\033[0m
- stop listening and exit: \033[1;30;107m ESC \033[0m
- send keyboard events as player: \033[1;30;107m 1 \033[0m \033[2m(default)\033[0m
- send keyboard events as host: \033[1;30;107m 0 \033[0m
- simulate player getting disconnected: \033[1;30;107m ENTER \033[0m
"""

LISTEN_WEB_MESSAGE = (
    "Connected to web, will not listen to local keyboard events.\n"
)
