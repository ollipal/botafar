from time import time as _time

from ... import __version__
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
    def __init__(
        self, send_event, callback_executor, on_initial_browser_connect
    ):
        self.send_event = send_event
        self.callback_executor = callback_executor
        self.on_initial_browser_connect = on_initial_browser_connect
        state_machine.reinit(
            self.inform, self.notify_state_change, callback_executor
        )
        self.browser_has_been_conected = False

    def process_event(self, event):  # noqa: C901
        if event._type == SYSTEM_EVENT:
            if event.name == "browser_connect":
                if not state_machine.browser_connected:
                    self.on_browser_connect(event.data)
                    state_machine.on_browser_connect()
            elif event.name == "browser_disconnect":
                if state_machine.browser_connected:
                    self.on_browser_disconnect()
                    state_machine.on_browser_disconnect()
            elif event.name == "owner_connect":
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
            elif event.name == "bot_behavior":
                bot_behavior = event.data.get("botBehavior")
                if bot_behavior is not None:
                    state_machine.on_bot_behavior_update(bot_behavior)
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

            if event.sender == "player":
                state_machine.latest_player_control_time = _time()
            elif event.sender == "owner":
                state_machine.latest_owner_control_time = _time()

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

    def notify_state_change(self, state, text=""):
        self.send_event(SystemEvent("state_change", state, text=text))

    def on_browser_connect(self, data):
        if not self.browser_has_been_conected:
            self.on_initial_browser_connect()
            self.browser_has_been_conected = True
        else:
            self.inform("browser connected")
        self.send_event(
            SystemEvent(
                "connect_ok", None, data=ControlBase._get_control_datas()
            )
        )
        latest_version = data.get("latestBotafarVersion")
        if latest_version is None:
            logger.debug("Could not read latestBotafarVersion")
        elif latest_version != __version__:
            self.inform(
                "botafar update available\ninstall with 'pip install "
                f"--upgrade botafar'\nCurrent version: {__version__}, "
                f"available {latest_version}\n"
                "changelog: https://docs.botafar.com/changelog"
            )

    def on_browser_disconnect(self):
        if state_machine.owner.is_connected:
            self.on_owner_disconnect()
            state_machine.on_owner_disconnect()

        if state_machine.player.is_connected:
            self.on_player_disconnect()
            state_machine.on_player_disconnect()

        self.inform("browser disconnected")

    def on_owner_connect(self):
        if state_machine.owner.is_connected:
            logger.debug("owner already connected")
            self.send_event(SystemEvent("already_connected", None))
            return

        if not state_machine.owner._is_controlling:
            state_machine.latest_owner_control_time = _time()
            state_machine.owner._is_controlling = True
            if state_machine.player._is_controlling:
                self.inform(
                    "owner took controls from "
                    f"'{state_machine.player.name}'"
                )
            else:
                self.inform("owner started controlling")

    def on_owner_disconnect(self):
        if not state_machine.owner.is_connected:
            logger.debug("owner already disconnected")
            return

        if state_machine.owner._is_controlling:
            state_machine.latest_player_control_time = _time()  # Reset player
            state_machine.owner._is_controlling = False
            if state_machine.player._is_controlling:
                self.inform(
                    "owner released controls back to "
                    f"'{state_machine.player.name}'"
                )
            else:
                self.inform("owner stopped controlling")

    def on_player_connect(self, name):
        state_machine.latest_player_control_time = _time()
        if state_machine.player.is_connected:
            logger.debug("Player already connected")
            return

        if not state_machine.browser_connected:
            # self.on_owner_connect()
            # state_machine.on_owner_connect()
            logger.warning("Player connected while browser disconnected... ")

        self.inform(f"'{name}' started controlling")

    def on_player_disconnect(self):
        if not state_machine.player.is_connected:
            logger.debug("Player already disconnected")
            return

        self.inform(f"'{state_machine.player.name}' stopped controlling")
