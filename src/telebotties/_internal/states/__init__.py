from .keyboard_client_state import KeyboardClientState
from .server_event_prosessor import ServerEventProsessor
from .server_state_machine import state_machine


# This allows .state directly
def __getattr__(name):
    if name == "state":
        return state_machine._state
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
