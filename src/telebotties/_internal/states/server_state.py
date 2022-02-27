from ..callbacks import CallbackBase
from ..constants import SYSTEM_EVENT
from ..inputs import InputBase
from ..log_formatter import get_logger

logger = get_logger()

IDENTITIES = [
    "player",
    "host",
]


class ServerState:
    def __init__(
        self, send_event, execute_callbacks, on_remote_client_connect
    ):
        self._send_event = send_event
        self._execute_callbacks = execute_callbacks
        self._on_remote_client_connect = on_remote_client_connect
        self._client_type = ""
        self._connected = False

    def process_event(self, event):
        if event._type == SYSTEM_EVENT:
            if (
                event.name == "client_connect"
                and event.value == "remote_keyboard"
            ):
                self._client_type = event.value
                self._on_remote_client_connect()
                self._connected = True
                logger.info(
                    f"{self._client_type.capitalize().replace('_',' ')} "
                    "connected"
                )
            elif event.name == "client_disconnect" and self._connected:
                self._connected = False
                logger.info(
                    f"{self._client_type.capitalize().replace('_',' ')} "
                    "disconnected"
                )

            callbacks = CallbackBase._get_callbacks(event)
            self._execute_callbacks(callbacks)  # TODO give time if needed?
        else:  # INPUT_EVENT
            callbacks = InputBase._get_callbacks(event)
            self._execute_callbacks(callbacks, event=event)
