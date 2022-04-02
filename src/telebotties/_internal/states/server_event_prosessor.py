from ..callbacks import CallbackBase
from ..constants import INPUT_EVENT, SYSTEM_EVENT
from ..inputs import InputBase
from ..log_formatter import get_logger
from .server_state_machine import state_machine

logger = get_logger()

IDENTITIES = [
    "player",
    "host",
]


class ServerEventProsessor:
    def __init__(self, send_event, execute_callbacks, on_remote_host_connect):
        state_machine.reinit(
            send_event, execute_callbacks, on_remote_host_connect
        )
        self._execute_callbacks = execute_callbacks

    def process_event(self, event):
        # Update input events, required...
        if event._type == INPUT_EVENT:
            event._update(True, -1)

        if event._type == SYSTEM_EVENT:
            if event.name == "host_connect":
                state_machine.on_host_connect()
            elif event.name == "host_disconnect":
                state_machine.on_host_disconnect()
            elif event.name == "player_connect":
                state_machine.on_player_connect()
            elif event.name == "player_disconnect":
                state_machine.on_player_disconnect()
            else:
                # TODO what exactly gets executed here?
                logger.warning(f"Excetuting unexpected event: {event}")
                callbacks = CallbackBase._get_callbacks(event)
                self._execute_callbacks(callbacks)  # TODO give time if needed?
        else:  # INPUT_EVENT
            callbacks = InputBase._get_callbacks(event)
            self._execute_callbacks(callbacks, event=event)
