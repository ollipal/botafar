from .keyboard_client_state import KeyboardClientState
from .server_event_prosessor import ServerEventProsessor
from .server_state_machine import (
    disable_controls,
    enable_controls,
    state_machine,
    stop,
)


# This allows .state .time .host .player directly
def __getattr__(name):
    if name == "state":
        return state_machine._state
    elif name == "host":
        return state_machine.host
    elif name == "player":
        return state_machine.player
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
