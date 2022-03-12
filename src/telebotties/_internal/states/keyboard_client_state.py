from ..constants import INPUT_EVENT, SYSTEM_EVENT
from ..events import SystemEvent
from ..log_formatter import get_logger

logger = get_logger()


class KeyboardClientState:
    def __init__(self, send_event):
        self._send_event = send_event

    def process_event(self, event):
        # Update input events, required...
        if event._type == INPUT_EVENT:
            event._update(True, -1)

        # Potentially send event before forwarding, modify
        # or block forwarding
        if event._type == SYSTEM_EVENT:
            if event.name == "already_connected":
                return
            if event.name == "client_disconnect":
                self._send("player_disconnect")
            elif event.name == "info":
                logger.info(event.text)
                return

        # Forward the event
        self._send_event(event)

        # And potentially send more
        if event._type == SYSTEM_EVENT:
            if event.name == "client_connect":
                self._send("player_connect")

    def _send(self, name):
        self._send_event(SystemEvent(name, "keyboard"))
