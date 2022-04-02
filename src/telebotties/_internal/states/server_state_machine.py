from dataclasses import dataclass

from transitions import Machine, State

from ..callbacks import CallbackBase
from ..log_formatter import get_logger

logger = get_logger()

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
        State(STOP_IMMEDIATE, ignore_invalid_triggers=True),
        STOP,
        State(EXIT_IMMEDIATE, ignore_invalid_triggers=True),
        EXIT,
    ]

    def __init__(self):
        self.host = Host()
        self.player = Player()
        self.machine = Machine(model=self, states=self.states, initial=INIT)

        # add_transition params: trigger, source, destination
        self.machine.add_transition(
            "wait_host",
            [INIT, STOP],
            WAITING_HOST,
            conditions="all_finished",
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
            after="after_waiting_player",
        )
        self.machine.add_transition(
            "start_before_controls",
            WAITING_PLAYER,
            START_BEFORE_CONTROLS,
            conditions="player_connected",
            after="after_start_before_controls",
        )
        self.machine.add_transition(
            "start",
            START_BEFORE_CONTROLS,
            START,
            # conditions="on_start_before_controls_finished",
            after="after_start",
        )
        self.machine.add_transition(
            "wait_stop",
            START,
            WAITING_STOP,
            # conditions="on_start_finished",
            after="after_waiting_stop",
        )
        self.machine.add_transition(
            "stop_immediate",
            [START_BEFORE_CONTROLS, START, WAITING_STOP],
            STOP_IMMEDIATE,
            after="after_stop_immediate",
        )  # when: stop() or player.disconnected
        self.machine.add_transition(
            "stop",
            STOP_IMMEDIATE,
            STOP,
            conditions="all_finished",
            after="after_stop",
        )
        self.machine.add_transition(
            "exit_immediate", "*", EXIT_IMMEDIATE, after="after_exit_immediate"
        )  # when: exit() or error
        self.machine.add_transition(
            "exit",
            EXIT_IMMEDIATE,
            EXIT,
            conditions="all_finished",
            after="after_exit",
        )

    # TODO maybe something smarter someday...
    def reinit(self, inform, callback_executor):
        self.inform = inform
        self.callback_executor = callback_executor

    # transition conditions requires this
    def host_connected(self):
        return self.host.connected

    # transition conditions requires this
    def player_connected(self):
        return self.player.connected

    def on_host_connect(self):
        self.host.connected = True
        if self.state == WAITING_HOST:
            self.prepare()
        elif self.state == WAITING_PLAYER:
            self.start_before_controls()

    def on_host_disconnect(self):
        self.host.connected = False
        if self.state in [START_BEFORE_CONTROLS, START, WAITING_STOP]:
            self.stop_immediate()

    def on_player_connect(self):
        self.player.connected = True
        if self.state == WAITING_PLAYER:
            self.start_before_controls()

    def on_player_disconnect(self):
        self.player.connected = False
        if self.state in [START_BEFORE_CONTROLS, START, WAITING_STOP]:
            self.stop_immediate()

    def all_finished(self):
        return len(self.callback_executor.running_names) == 0

    def execute(self, name, callback):
        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name(name), name, callback
        )

    def after_waiting_host(self):
        logger.debug("STATE: waiting_host")
        if self.host.connected:
            self.prepare()

    def after_prepare(self):
        logger.debug("STATE: prepare")
        self.execute("on_prepare", self.wait_player)

    def after_waiting_player(self):
        logger.debug("STATE: waiting_player")
        if self.player.connected:
            self.start_before_controls()

    def after_start_before_controls(self):
        logger.debug("STATE: start_before_controls")
        self.execute("on_start_before_controls", self.start)

    def after_start(self):
        logger.debug("STATE: start")
        self.enable_controls()
        self.execute("on_start", self.wait_stop)

    def after_waiting_stop(self):
        logger.debug("STATE: waiting_stop")
        # .stop_immediate() will be triggered from outside

    def after_stop_immediate(self):
        logger.debug("STATE: stop_immediate")
        self.disable_controls()
        self.execute("on_stop_immediate", self.stop)

    def after_stop(self):
        logger.debug("STATE: stop")
        self.execute("on_stop", self.wait_host)

    def after_exit_immediate(self):
        logger.debug("STATE: exit_immediate")
        # "on_exit_immediate" executed from main

    def after_exit(self):
        logger.debug("STATE: exit")
        # "on_exit" executed from main

    def on_input_finished_callback(self):
        if self.state == STOP_IMMEDIATE and self.all_finished:
            self.stop()
        elif self.state == EXIT_IMMEDIATE and self.all_finished:
            self.exit()

    def enable_controls(self):
        if not self.player.controlling:
            self.player.controlling = True
            self.inform("controls enabled")

    def disable_controls(self):
        if self.player.controlling:
            self.player.controlling = False
            self.inform("controls disabled")

    @property
    def _state(self):  # name 'state' is reserved by transitions
        return SIMPLIFIED_STATES.get(self.state, self.state)


state_machine = ServerStateMachine()
