from ..callbacks import CallbackBase
from ..constants import INPUT_EVENT, SYSTEM_EVENT
from ..events import SystemEvent
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
        self._player_connected = False

    def process_event(self, event):
        # Update input events, required...
        if event._type == INPUT_EVENT:
            event._update(True, -1)

        if event._type == SYSTEM_EVENT:
            if event.name == "client_connect" and self._connected:
                self._send_event(SystemEvent("already_connected", None))
                return
            elif event.name == "client_connect" and not self._connected:
                self._client_type = event.value
                self._on_remote_client_connect()
                self._connected = True
                self._send_event(SystemEvent("connect_ok", None))
                message = "client connected"
                logger.info(message)
                self._send_event(SystemEvent("info", None, message))
            elif event.name == "client_disconnect" and self._connected:
                self._connected = False
                message = "client disconnected"
                logger.info(message)
                self._send_event(SystemEvent("info", None, message))
            elif event.name == "player_connect" and not self._player_connected:
                self._player_connected = True
                message = "player connected"
                logger.info(message)
                self._send_event(SystemEvent("info", None, message))
            elif event.name == "player_disconnect" and self._player_connected:
                self._player_connected = False
                message = "player disconnected"
                logger.info(message)
                self._send_event(SystemEvent("info", None, message))

            callbacks = CallbackBase._get_callbacks(event)
            self._execute_callbacks(callbacks)  # TODO give time if needed?
        else:  # INPUT_EVENT
            callbacks = InputBase._get_callbacks(event)
            self._execute_callbacks(callbacks, event=event)
