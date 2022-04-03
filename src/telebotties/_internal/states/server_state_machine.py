from threading import RLock
from time import time as _time

from transitions import Machine, State, core

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


class Host:
    def __init__(self):
        self._is_connected = False
        self._is_controlling = False
        self._name = ""

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def is_controlling(self):
        return self._is_controlling

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return (
            f"Host(name='{self.name}', is_connected={self.is_connected}, "
            f"is_controlling={self.is_controlling})"
        )


class Player:
    def __init__(self):
        self._is_connected = False
        self._is_controlling = False
        self._name = ""

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def is_controlling(self):
        return self._is_controlling

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return (
            f"Player(name='{self.name}', is_connected={self.is_connected}, "
            f"is_controlling={self.is_controlling})"
        )


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
        self.start_time = -1
        self.machine = Machine(model=self, states=self.states, initial=INIT)
        self.rlock = RLock()

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
            conditions=["host_connected", "player_connected"],
            after="after_start_before_controls",
        )
        self.machine.add_transition(
            "start",
            START_BEFORE_CONTROLS,
            START,
            conditions=["host_connected", "player_connected"],
            after="after_start",
        )
        self.machine.add_transition(
            "wait_stop",
            START,
            WAITING_STOP,
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

    def all_finished(self):
        running_names = self.callback_executor.running_names
        if len(running_names) != 0:
            logger.debug(f"Running: {running_names}")
        return len(running_names) == 0

    def execute(self, name, callback, callback_name):
        def safe_callback():
            self.safe_state_change(callback, callback_name)

        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name(name), name, safe_callback
        )

    def safe_state_change(self, function, name):
        try:
            function()
        except core.MachineError:
            logger.debug(f"Transition '{name}' skipped")

    def synced_stop(self):
        # This hopefully addresses the theoritcally possible
        # chance that someone calls .stop() or .exit() between
        # the if state check
        with self.rlock:
            if self.state == STOP_IMMEDIATE:
                self.stop()

    def synced_exit(self):
        # This hopefully addresses the theoritcally possible
        # chance that someone calls .stop() or .exit() between
        # the if state check
        with self.rlock:
            if self.state == EXIT_IMMEDIATE:
                self.exit()

    # transition conditions requires this
    def host_connected(self):
        return self.host.is_connected

    # transition conditions requires this
    def player_connected(self):
        return self.player.is_connected

    def on_host_connect(self, name):
        self.host._name = name
        self.host._is_connected = True
        # if self.state == WAITING_HOST:
        self.safe_state_change(self.prepare, "prepare")
        # elif self.state == WAITING_PLAYER:
        self.safe_state_change(
            self.start_before_controls, "start_before_controls"
        )

    def on_host_disconnect(self):
        self.host._name = ""
        self.host._is_connected = False
        # if self.state in [START_BEFORE_CONTROLS, START, WAITING_STOP]:
        self.safe_state_change(self.stop_immediate, "stop_immediate")

    def on_player_connect(self, name):
        self.player._name = name
        self.player._is_connected = True
        # if self.state == WAITING_PLAYER:
        self.safe_state_change(
            self.start_before_controls, "start_before_controls"
        )

    def on_player_disconnect(self):
        self.player._name = ""
        self.player._is_connected = False
        # if self.state in [START_BEFORE_CONTROLS, START, WAITING_STOP]:
        self.safe_state_change(self.stop_immediate, "stop_immediate")

    def after_waiting_host(self):
        logger.debug("STATE: waiting_host")
        # if self.host.connected:
        self.prepare()

    def after_prepare(self):
        logger.debug("STATE: prepare")
        self.execute("on_prepare", self.wait_player, "wait_player")

    def after_waiting_player(self):
        logger.debug("STATE: waiting_player")
        # if self.player.connected:
        self.start_before_controls()

    def after_start_before_controls(self):
        logger.debug("STATE: start_before_controls")
        self.start_time = _time()
        logger.debug(self.start_time)
        self.execute("on_start_before_controls", self.start, "start")

    def after_start(self):
        logger.debug("STATE: start")
        self.enable_controls()

        def on_start_callback():
            self.wait_stop()
            self.synced_stop()

        self.execute("on_start", on_start_callback, "on_start_callback")

    def after_waiting_stop(self):
        logger.debug("STATE: waiting_stop")
        # .stop_immediate() will be triggered from outside

    def after_stop_immediate(self):
        logger.debug("STATE: stop_immediate")
        self.disable_controls()
        self.execute("on_stop_immediate", self.synced_stop, "synced_stop")

    def after_stop(self):
        logger.debug("STATE: stop")
        self.start_time = -1
        self.execute("on_stop", self.wait_host, "wait_host")

    def after_exit_immediate(self):
        logger.debug("STATE: exit_immediate")
        # "on_exit_immediate" executed from main

    def after_exit(self):
        logger.debug("STATE: exit")
        self.start_time = -1
        # "on_exit" executed from main

    def on_input_finished_callback(self):
        if self.state == STOP_IMMEDIATE and self.all_finished:
            self.safe_state_change(self.synced_stop, "synced_stop")
        # "synced_exit" executed from main

    def enable_controls(self):
        if not self.player.is_controlling:
            self.player._is_controlling = True
            self.inform("controls enabled")

    def disable_controls(self):
        if self.player.is_controlling:
            self.player._is_controlling = False
            if self.player.is_connected:
                self.inform("controls disabled")

    def _state(self):  # name 'state' is reserved by transitions
        return SIMPLIFIED_STATES.get(self.state, self.state)

    def time(self):
        if self.start_time == -1:
            return -1
        else:
            return round(_time() - self.start_time, 2)


state_machine = ServerStateMachine()

state = state_machine._state
time = state_machine.time
host = state_machine.host
player = state_machine.player
enable_controls = state_machine.enable_controls
disable_controls = state_machine.disable_controls
stop = state_machine.stop_immediate