from dataclasses import dataclass

from transitions import Machine

from ..events import SystemEvent
from ..inputs import InputBase
from ..log_formatter import get_logger

logger = get_logger()

PRE_INIT = "pre_init"
INIT = "init"
WAITING_HOST = "waiting_host"
PREPARE = "prepare"
WAITING_PLAYER = "waiting_player"
START_BEFORE_CONTROLS = "start_before_controls"
START = "start"
WAITING_STOP = "waiting_stop"
STOP_IMMEDIATE = "stop_immediate"
STOP = "stop"
EXIT_IMMEDIATE = "exit_immediate"
EXIT = "exit"

SIMPLIFIED_STATES = {
    PRE_INIT: "init",
    START_BEFORE_CONTROLS: "start",
    STOP_IMMEDIATE: "stop",
    EXIT_IMMEDIATE: "exit",
}


# TODO block writing values
@dataclass
class Host:
    connected: bool = False
    controlling: bool = False
    name: str = ""


# TODO block writing values
@dataclass
class Player:
    connected: bool = False
    controlling: bool = False
    name: str = ""


class ServerStateMachine:
    states = [
        INIT,
        WAITING_HOST,
        PREPARE,
        WAITING_PLAYER,
        START_BEFORE_CONTROLS,
        START,
        WAITING_STOP,
        STOP_IMMEDIATE,
        STOP,
        EXIT_IMMEDIATE,
        EXIT,
    ]

    def __init__(self):
        self.host = Host()
        self.player = Player()
        self.machine = Machine(
            model=self, states=self.states, initial=PRE_INIT
        )

        # add_transition params: trigger, source, destination
        self.machine.add_transition(
            "init",
            PRE_INIT,
            INIT,
            after="after_init",
        )
        self.machine.add_transition(
            "wait_host",
            INIT,
            WAITING_HOST,
            conditions="on_init_finished",
            after="after_waiting_host",
        )
        self.machine.add_transition(
            "prepare",
            WAITING_HOST,
            PREPARE,
            conditions="host_connected",
            after="after_prepare",
        )
        self.machine.add_transition(
            "wait_player",
            PREPARE,
            WAITING_PLAYER,
            conditions="on_prepare_finished",
        )
        self.machine.add_transition(
            "start_before_contorls",
            WAITING_PLAYER,
            START_BEFORE_CONTROLS,
            conditions="player_connected",
            after="after_start_before_contorls",
        )
        self.machine.add_transition(
            "start",
            START_BEFORE_CONTROLS,
            START,
            conditions="on_start_bofore_controls_finished",
            after="after_start",
        )
        self.machine.add_transition(
            "wait_stop", START, WAITING_STOP, conditions="on_start_finished"
        )
        self.machine.add_transition(
            "stop_immediate", [START, WAITING_STOP], STOP_IMMEDIATE
        )  # when: stop() or player_disconnected
        self.machine.add_transition(
            "stop",
            STOP_IMMEDIATE,
            STOP,
            conditions=["on_start_finished", "on_input_finished"],
            after="after_stop",
        )
        self.machine.add_transition(
            "exit_immediate", "*", EXIT_IMMEDIATE
        )  # when: exit() or error
        self.machine.add_transition(
            "exit",
            EXIT_IMMEDIATE,
            EXIT,
            conditions="all_finished",
            after="after_exit",
        )

    # TODO maybe something smarter someday...
    def reinit(self, send_event, execute_callbacks, on_remote_host_connect):
        self._send_event = send_event
        self._execute_callbacks = execute_callbacks
        self._on_remote_host_connect = on_remote_host_connect

    # transition conditions requires this
    def host_connected(self):
        return self.host.connected

    # transition conditions requires this
    def player_connected(self):
        return self.player.connected

    def on_host_connect(self):
        if self.host.connected:
            logger.debug("Host already connected")
            self._send_event(SystemEvent("already_connected", None))
            return

        self.host.connected = True
        self._on_remote_host_connect()
        self._send_event(
            SystemEvent("connect_ok", None, data=InputBase._get_input_datas())
        )
        message = "host connected"
        logger.info(message)
        self._send_event(SystemEvent("info", None, message))

    def on_host_disconnect(self):
        if not self.host.connected:
            logger.debug("Host already disconnected")
            return

        self.host.connected = False
        if self.player.connected:
            self.on_player_disconnect()
        message = "host disconnected"
        logger.info(message)
        self._send_event(SystemEvent("info", None, message))

    def on_player_connect(self):
        if self.player.connected:
            logger.debug("Player already connected")
            return

        self.player.connected = True
        message = "player connected"
        logger.info(message)
        self._send_event(SystemEvent("info", None, message))

    def on_player_disconnect(self):
        if not self.player.connected:
            logger.debug("Player already disconnected")
            return

        self.player.connected = False
        message = "player disconnected"
        logger.info(message)
        self._send_event(SystemEvent("info", None, message))

    def on_init_finished(self):
        return True

    def on_prepare_finished(self):
        return True

    def on_start_bofore_controls_finished(self):
        return True

    def on_start_finished(self):
        return True

    def on_input_finished(self):
        return True

    def all_finished(self):
        return True

    ##
    """def on_host_connect(self):
        self.host.connected = True
        if self.state == WAITING_HOST:
            self.prepare()
        if self.state == WAITING_PLAYER:
            self.start()

    def on_host_disconnect(self):
        self.host.connected = False
        if self.state in [START, WAITING_STOP]:
            self.stop_immediate()

    def on_player_connect(self):
        self.player.connected = True
        self.prepare()

    def on_player_disconnect(self):
        self.player.connected = False
        if self.state in [START, WAITING_STOP]:
            self.stop_immediate()
    """

    def after_init(self):
        logger.info("after init!")
        # run: on_init, after: wait_host

    def after_waiting_host(self):
        logger.info("after waiting_host!")
        # if host.connected: prepare()

    def after_prepare(self):
        logger.info("after prepare!")
        # run: on_prepare, after: wait_player()

    def after_waiting_player(self):
        logger.info("after waiting_host!")
        # if player.connected: start_immediate()

    def after_start_before_controls(self):
        logger.info("after start before controls!")
        # run: on_start_immediate, after: on_start()

    def after_start(self):
        logger.info("after start!")
        # run: on_start, after: wait_stop()

    # after on_stop not needed?
    # MAKE SURE ON_START DOES NOT GET SKIPPED

    def after_stop(self):
        logger.info("after stop!")
        # run: on_stop, after: wait_host()

    def after_exit(self):
        logger.info("after exit!")

    def enable_inputs(self):
        logger.info("enabling inputs")

    def disable_inputs(self):
        logger.info("disabling inputs")

    @property
    def _state(self):  # name 'state' is reserved by transitions
        return SIMPLIFIED_STATES.get(self.state, self.state)


state_machine = ServerStateMachine()

if __name__ == "__main__":
    s = state_machine
    print(s._state)
    s.init()
    print(s._state)
    s.wait_host()
    print(s._state)
    s.prepare()
    print(s._state)
    s.host_connected = True
    s.prepare()
    print(s._state)
    s.exit_immediate()
    print(s._state)
    s.exit()
    print(s._state)
