from ..constants import SYSTEM_EVENT
from ..events import SystemEvent
from ..inputs import InputBase
from ..log_formatter import get_logger
from .server_state_machine import state_machine

logger = get_logger()

IDENTITIES = [
    "player",
    "host",
]


class ServerEventProsessor:
    def __init__(self, send_event, callback_executor, on_remote_host_connect):
        self.send_event = send_event
        self.callback_executor = callback_executor
        self.on_remote_host_connect = on_remote_host_connect
        state_machine.reinit(self.inform, callback_executor)

    def process_event(self, event):
        if event._type == SYSTEM_EVENT:
            if event.name == "host_connect":
                if not state_machine.host.connected:
                    self.on_host_connect()
                    state_machine.on_host_connect()
            elif event.name == "host_disconnect":
                if state_machine.host.connected:
                    self.on_host_disconnect()
                    state_machine.on_host_disconnect()
            elif event.name == "player_connect":
                if not state_machine.player.connected:
                    self.on_player_connect()
                    state_machine.on_player_connect()
            elif event.name == "player_disconnect":
                if state_machine.player.connected:
                    self.on_player_disconnect()
                    state_machine.on_player_disconnect()
            else:
                logger.warning(f"Unknown system event? {event.name}")
        else:  # INPUT_EVENT
            # Update input events, required...
            event._update(True, -1)

            if (
                event.sender == "player"
                and not state_machine.player.controlling
            ):
                logger.debug("Player controls disabled, skipping")
                return

            callbacks = InputBase._get_callbacks(event)
            self.callback_executor.execute_callbacks(
                callbacks,
                event.name,
                state_machine.on_input_finished_callback,
                event=event,
            )

    def inform(self, message):
        logger.info(message)
        self.send_event(SystemEvent("info", None, message))

    def on_host_connect(self):
        if state_machine.host.connected:
            logger.debug("Host already connected")
            self.send_event(SystemEvent("already_connected", None))
            return

        self.on_remote_host_connect()
        self.send_event(
            SystemEvent("connect_ok", None, data=InputBase._get_input_datas())
        )
        self.inform("host connected")

    def on_host_disconnect(self):
        if not state_machine.host.connected:
            logger.debug("Host already disconnected")
            return

        if state_machine.player.connected:
            self.on_player_disconnect()
            state_machine.on_player_disconnect()

        self.inform("host disconnected")

    def on_player_connect(self):
        if state_machine.player.connected:
            logger.debug("Player already connected")
            return

        self.inform("player connected")

    def on_player_disconnect(self):
        if not state_machine.player.connected:
            logger.debug("Player already disconnected")
            return

        self.inform("player disconnected")
