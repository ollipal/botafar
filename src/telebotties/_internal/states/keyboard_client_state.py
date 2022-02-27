from ..constants import INPUT_EVENT, SYSTEM_EVENT
from ..events import SystemEvent
from ..log_formatter import get_logger

logger = get_logger()

IDENTITIES = [
    "player",
    "host",
]


class KeyboardClientState:
    def __init__(self, send_event):
        self._identity_index = 0
        self._send_event = send_event

    def process_event(self, event):
        # Update input events, required...
        if event._type == INPUT_EVENT:
            event._update(True, -1)

        # Potentially send event before forwarding, modify
        # or block forwarding
        if event._type == SYSTEM_EVENT:
            if event.name == "client_connect":
                event.set_value("remote_keyboard")
            elif event.name == "client_disconnect":
                self._send(f"{self._identity}_disconnect")
            elif event.name == "keyboard_tab":
                # Old disconnect
                self._send(f"{self._identity}_disconnect")
                # Change
                if self._identity_index == len(IDENTITIES) - 1:
                    self._identity_index = 0
                else:
                    self._identity_index += 1
                # New Connect
                self._send(f"{self._identity}_connect")
                logger.info(f"Connected as {self._identity}")
                return

        # Forward the event
        self._send_event(event)

        # And potentially send more
        if event._type == SYSTEM_EVENT:
            if event.name == "client_connect":
                self._send(f"{self._identity}_connect")
                logger.info(f"Connected as {self._identity}")

    @property
    def _identity(self):
        return IDENTITIES[self._identity_index]

    def _send(self, name):
        self._send_event(SystemEvent(name, "keyboard"))
