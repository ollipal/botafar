from ..constants import SYSTEM_EVENT
from ..events import SystemEvent
from ..log_formatter import get_logger

logger = get_logger()


class KeyboardClientState:
    def __init__(self, send_event, end_callback):
        self.send_event = send_event
        self.end_callback = end_callback
        self.player_connected = False

    def process_event(self, event):
        """Return True if should stop"""

        # Potentially send event before forwarding, modify
        # or block forwarding
        if event._type == SYSTEM_EVENT:
            if event.name == "already_connected":
                return
            elif event.name == "owner_disconnect":
                if self.player_connected:
                    # Blocks forwarded messages
                    self.player_connected = False
                    # Write them yourself
                    # logger.info("player disconnected")
                    # logger.info("owner disconnected")
                self.end_callback()
                return
            elif event.name == "print":
                print(event.value)
                return
            elif event.name == "info":
                if self.player_connected:
                    logger.info(event.text)
                    return
            elif event.name == "error":
                logger.error(event.text)
                self.end_callback()
                return
            elif event.name == "state_change":
                logger.debug(f"STATE: {event.value}")
                if event.value == "waiting_player":
                    self.player_connected = True
                    self.send_event(SystemEvent("player_connect", "player"))
                return
            else:
                logger.debug(f"Unknown handled: {event}")

        # Forward the event
        self.send_event(event)

        # And potentially send more
        if event._type == SYSTEM_EVENT:
            if event.name == "owner_connect":
                logger.debug("owner connected")
