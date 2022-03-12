from ..constants import INPUT_EVENT, SYSTEM_EVENT
from ..events import SystemEvent
from ..log_formatter import get_logger

logger = get_logger()


class KeyboardClientState:
    def __init__(self, send_event):
        self._send_event = send_event
        self._player_connected = False

    def process_event(self, event):
        # Update input events, required...
        if event._type == INPUT_EVENT:
            event._update(True, -1)

        # Potentially send event before forwarding, modify
        # or block forwarding
        if event._type == SYSTEM_EVENT:
            if event.name == "already_connected":
                return
            elif event.name == "client_disconnect":
                # self._send("player_disconnect")
                # Blocks forwarded messages
                self._player_connected = False
                # Write them yourself
                logger.info("player disconnected")
                logger.info("client disconnected")
                return
            elif event.name == "info":
                if self._player_connected:
                    logger.info(event.text)
                    return

        # Forward the event
        self._send_event(event)

        # And potentially send more
        if event._type == SYSTEM_EVENT:
            if event.name == "client_connect":
                self._player_connected = True
                self._send("player_connect")

    def _send(self, name):
        self._send_event(SystemEvent(name, "keyboard"))
