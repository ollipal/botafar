from platform import system

from .string_utils import dim, key

is_windows = system().lower() == "windows"

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

SENDERS = {"player", "owner"}
ORIGINS = {"keyboard", "screen"}

INPUT_EVENT = "INPUT_EVENT"
SYSTEM_EVENT = "SYSTEM_EVENT"

LISTEN_BROWSER_MESSAGE = (
    f"Browser connected, press " f"{key('Ctrl')} + {key('C')} to exit."
)

SIGINT_MESSAGE = (
    f"\n{key('Ctrl')} + {key('C')} received, "
    f"shutting down gracefully... {dim('(Press again to exit immediately)')}"
)
