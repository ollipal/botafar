from ..constants import SYSTEM_EVENT
from ..controls import ControlBase
from ..events import SystemEvent
from ..log_formatter import get_logger
from .server_state_machine import state_machine

logger = get_logger()

IDENTITIES = [
    "player",
    "owner",
]


class ServerEventProsessor:
    def __init__(self, send_event, callback_executor, on_remote_owner_connect):
        self.send_event = send_event
        self.callback_executor = callback_executor
        self.on_remote_owner_connect = on_remote_owner_connect
        state_machine.reinit(
            self.inform, self.notify_state_change, callback_executor
        )

    def process_event(self, event):
        if event._type == SYSTEM_EVENT:
            if event.name == "owner_connect":
                if not state_machine.owner.is_connected:
                    self.on_owner_connect()
                    state_machine.on_owner_connect()
            elif event.name == "owner_disconnect":
                if state_machine.owner.is_connected:
                    self.on_owner_disconnect()
                    state_machine.on_owner_disconnect()
            elif event.name == "player_connect":
                if not state_machine.player.is_connected:
                    name = event.value
                    self.on_player_connect(name)
                    state_machine.on_player_connect(name)
            elif event.name == "player_disconnect":
                if state_machine.player.is_connected:
                    self.on_player_disconnect()
                    state_machine.on_player_disconnect()
            elif event.name == "owner_start_controlling":
                if not state_machine.owner.is_controlling:
                    state_machine.owner._is_controlling = True
                    if state_machine.player._is_controlling:
                        self.inform(
                            "owner took controls from "
                            f"'{state_machine.player.name}'"
                        )
                    else:
                        self.inform("owner started controlling")
            elif event.name == "owner_stop_controlling":
                if state_machine.owner.is_controlling:
                    state_machine.owner._is_controlling = False
                    if state_machine.player._is_controlling:
                        self.inform(
                            "owner released controls back to "
                            f"'{state_machine.player.name}'"
                        )
                    else:
                        self.inform("owner stopped controlling")
            elif event.name == "info":
                pass
            else:
                logger.warning(f"Unknown system event {event.name}")
        else:  # INPUT_EVENT
            if (
                event.sender == "player"
                and not state_machine.player._is_controlling
            ):
                logger.debug("Player controls disabled, skipping")
                return

            event._set_time(state_machine.time())
            callbacks = ControlBase._get_callbacks(event)

            self.callback_executor.execute_callbacks(
                callbacks,
                event.name,
                state_machine.on_control_finished_callback,
                event=event,
            )

    def inform(self, message):
        logger.info(message)
        self.send_event(SystemEvent("info", None, message))

    def notify_state_change(self, state):
        self.send_event(SystemEvent("state_change", state, ""))

    def on_owner_connect(self):
        if state_machine.owner.is_connected:
            logger.debug("owner already connected")
            self.send_event(SystemEvent("already_connected", None))
            return

        self.on_remote_owner_connect()
        self.send_event(
            SystemEvent(
                "connect_ok", None, data=ControlBase._get_control_datas()
            )
        )
        # self.inform("owner connected")

    def on_owner_disconnect(self):
        if not state_machine.owner.is_connected:
            logger.debug("owner already disconnected")
            return

        if state_machine.player.is_connected:
            self.on_player_disconnect()
            state_machine.on_player_disconnect()

        # self.inform("owner disconnected")

    def on_player_connect(self, name):
        if state_machine.player.is_connected:
            logger.debug("Player already connected")
            return

        if not state_machine.owner.is_connected:
            self.on_owner_connect()
            state_machine.on_owner_connect()
            logger.warning("Player connected while owner disconnected... ")

        self.inform(f"'{name}' started controlling")

    def on_player_disconnect(self):
        if not state_machine.player.is_connected:
            logger.debug("Player already disconnected")
            return

        self.inform(f"'{state_machine.player.name}' stopped controlling")
