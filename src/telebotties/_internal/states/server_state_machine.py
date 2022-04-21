import asyncio
import threading
from time import time as _time

from transitions import Machine
from transitions import State as State_
from transitions import core

from ..callbacks import CallbackBase
from ..controls import ControlBase
from ..exceptions import SleepCancelledError
from ..log_formatter import get_logger

logger = get_logger()


PRE_INIT = "pre_init"
INIT = "on_init"
WAITING_HOST = "waiting_host"
PREPARE = "on_prepare"
WAITING_PLAYER = "waiting_player"
START = "on_start"
WAITING_STOP = "waiting_stop"
STOP_IMMEDIATE = "stop_immediate"
STOP = "on_stop"
EXIT_IMMEDIATE = "exit_immediate"
EXIT = "on_exit"

SIMPLIFIED_STATES = {
    PRE_INIT: INIT,
    WAITING_STOP: START,
    STOP_IMMEDIATE: STOP,
    EXIT_IMMEDIATE: EXIT,
}


class Host:
    def __init__(self):
        self._is_connected = False
        self._is_controlling_player = False
        self._is_controlling_host_only = False
        self._name = ""

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"Host(name='{self.name}', is_connected={self.is_connected})"


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


class State:
    def __init__(self, state_machine):
        self._state_machine = state_machine

    @property
    def is_initializing(self):
        return self._state_machine._state() == INIT

    @property
    def is_waiting_host(self):
        return self._state_machine._state() == WAITING_HOST

    @property
    def is_preparing(self):
        return self._state_machine._state() == PREPARE

    @property
    def is_waiting_player(self):
        return self._state_machine._state() == WAITING_PLAYER

    @property
    def is_starting(self):
        return self._state_machine._state() == START

    @property
    def is_stopping(self):
        return self._state_machine._state() == STOP

    @property
    def is_exiting(self):
        return self._state_machine._state() == EXIT

    def __repr__(self):
        if self.is_initializing:
            return "State(is_initializing=True)"
        elif self.is_waiting_host:
            return "State(is_waiting_host=True)"
        elif self.is_preparing:
            return "State(is_preparing=True)"
        elif self.is_waiting_player:
            return "State(is_waiting_player=True)"
        elif self.is_starting:
            return "State(is_starting=True)"
        elif self.is_stopping:
            return "State(is_stopping=True)"
        elif self.is_exiting:
            return "State(is_exiting=True)"
        else:
            raise RuntimeError("Unknown state, should not happen")


class ServerStateMachine:
    states = [
        PRE_INIT,
        INIT,
        WAITING_HOST,
        PREPARE,
        WAITING_PLAYER,
        START,
        WAITING_STOP,
        State_(STOP_IMMEDIATE, ignore_invalid_triggers=True),
        STOP,
        State_(EXIT_IMMEDIATE, ignore_invalid_triggers=True),
        EXIT,
    ]

    def __init__(self):
        self.host = Host()
        self.player = Player()
        self.start_time = -1
        self.machine = Machine(
            model=self, states=self.states, initial=PRE_INIT
        )

        # At least 'all_finished' and 'reset_controls'
        # needs to be synced as it might otherwise show
        # all_finished too early, others might be unnecessary
        self.rlock = threading.RLock()
        self.sleep_event_sync = threading.Event()
        self.sleep_event_async = None  # Added later when the loop starts
        self.callback_executor = None  # Added later also

        # add_transition params: trigger, source, destination
        self.machine.add_transition(
            "init",
            PRE_INIT,
            INIT,
            after="after_init",
        )
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
            "start",
            WAITING_PLAYER,
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
            [START, WAITING_STOP],
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
    def reinit(self, inform, notify_state_change, callback_executor):
        self.inform = inform
        self.notify_state_change = notify_state_change
        self.callback_executor = callback_executor

    def all_finished(self):
        with self.rlock:
            running_names = self.callback_executor.running_names
            if len(running_names) != 0:
                logger.debug(f"Running: {running_names}")
            return len(running_names) == 0

    def execute(self, name, callback, callback_name):
        def safe_callback():
            self.safe_state_change(callback, callback_name, name)

        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name(name), name, safe_callback
        )

    def safe_state_change(self, function, name, origin):
        try:
            function()
        except core.MachineError:
            logger.debug(f"Transition '{name}' skipped (origin: {origin})")

    def synced_stop(self):
        # This hopefully addresses the theoritcally possible
        # chance that someone calls .stop() or .exit() between
        # the if state check
        with self.rlock:
            if self.state == STOP_IMMEDIATE:
                self.stop()  # Attempt going forward

    def synced_exit(self):
        # This hopefully addresses the theoritcally possible
        # chance that someone calls .stop() or .exit() between
        # the if state check
        with self.rlock:
            if self.state == EXIT_IMMEDIATE:
                self.exit()  # Attempt going forward

    # transition conditions requires this
    def host_connected(self):
        # with self.rlock:
        return self.host.is_connected

    # transition conditions requires this
    def player_connected(self):
        # with self.rlock:
        return self.player.is_connected

    def on_host_connect(self, name):
        # with self.rlock:
        self.host._name = name
        self.host._is_connected = True
        # if self.state == WAITING_HOST:
        self.safe_state_change(self.prepare, "prepare", "host_connect")
        # elif self.state == WAITING_PLAYER:
        self.safe_state_change(self.start, "start", "host_connect")

    def on_host_disconnect(self):
        # with self.rlock:
        self.host._name = ""
        self.host._is_connected = False
        # if self.state in [START, WAITING_STOP]:
        self.safe_state_change(
            self.stop_immediate, "stop_immediate", "host_disconnect"
        )

    def on_player_connect(self, name):
        # with self.rlock:
        self.player._name = name
        self.player._is_connected = True
        # if self.state == WAITING_PLAYER:
        self.safe_state_change(self.start, "start", "player_connect")

    def on_player_disconnect(self):
        # with self.rlock:
        self.player._name = ""
        self.player._is_connected = False
        # if self.state in [START, WAITING_STOP]:
        self.safe_state_change(
            self.stop_immediate, "stop_immediate", "player_disconnect"
        )

    def after_init(self):
        # with self.rlock:
        logger.debug("STATE: on_init")
        # NOTE: not notify_state_change, no one connected yet
        # "on_init" executed from main

    def after_waiting_host(self):
        # with self.rlock:
        logger.debug("STATE: waiting_host")
        self.notify_state_change("waiting_host")
        self.start_time = -1
        # if self.host.connected:
        self.prepare()

    def after_prepare(self):
        # with self.rlock:
        logger.debug("STATE: on_prepare")
        self.notify_state_change("on_prepare")

        def safe_on_prepare_callback():
            self.safe_state_change(
                self.wait_player, "wait_player", "on_prepare"
            )
            self.safe_state_change(
                self.synced_stop, "synced_stop", "on_prepare"
            )
            self.safe_state_change(
                self.synced_exit, "synced_exit", "on_prepare"
            )

        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name("on_prepare"),
            "on_prepare",
            safe_on_prepare_callback,
        )

    def after_waiting_player(self):
        # with self.rlock:
        logger.debug("STATE: waiting_player")
        self.notify_state_change("waiting_player")
        # if self.player.connected:
        self.start()

    def after_start(self):
        # with self.rlock:
        logger.debug("STATE: on_start")
        self.notify_state_change("on_start")
        self.enable_controls()
        self.start_time = _time()
        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name("on_time"),
            "on_time",
            self.on_repeat_or_time_finished_callback,
        )
        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name("on_repeat"),
            "on_repeat",
            self.on_repeat_or_time_finished_callback,
        )

        def safe_on_start_callback():
            self.safe_state_change(self.wait_stop, "wait_stop", "on_start")
            self.safe_state_change(self.synced_stop, "synced_stop", "on_start")
            self.safe_state_change(self.synced_exit, "synced_exit", "on_start")

        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name("on_start"),
            "on_start",
            safe_on_start_callback,
        )

    def after_waiting_stop(self):
        # with self.rlock:
        logger.debug("STATE: waiting_stop")
        # NOTE: not notify_state_change, state hidden from the user
        # .stop_immediate() will be triggered from outside

    def after_stop_immediate(self):
        # with self.rlock:
        logger.debug("STATE: stop_immediate")
        self.notify_state_change("on_stop")
        self.sleep_event_sync.set()
        self.sleep_event_async.set()
        self.disable_controls()
        self.execute("on_stop_immediate", self.synced_stop, "synced_stop")

    def after_stop(self):
        # with self.rlock:
        logger.debug("STATE: stop")
        self.sleep_event_sync.clear()
        self.sleep_event_async.clear()
        self.execute("on_stop", self.wait_host, "wait_host")

    def after_exit_immediate(self):
        # with self.rlock:
        logger.debug("STATE: exit_immediate")
        self.notify_state_change("on_exit")
        self.sleep_event_sync.set()
        self.sleep_event_async.set()
        self.disable_controls()
        self.reset_controls("host")
        # "on_exit_immediate" executed from main

    def after_exit(self):
        # with self.rlock:
        self.sleep_event_sync.clear()
        self.sleep_event_async.clear()
        logger.debug("STATE: exit")
        self.start_time = -1
        # "on_exit" executed from main

    def on_control_finished_callback(self):
        # Perf reasons, this is executed a lot
        if self.state not in [STOP_IMMEDIATE, STOP]:
            return

        with self.rlock:
            if self.all_finished():
                if self.state == STOP_IMMEDIATE:
                    self.safe_state_change(
                        self.synced_stop, "synced_stop", "control_finished"
                    )
                elif self.state == STOP:
                    self.safe_state_change(
                        self.wait_host, "wait_host", "control_finished"
                    )
        # "synced_exit" executed from main

    def on_repeat_or_time_finished_callback(self):
        self.on_control_finished_callback()

    def enable_controls(self):
        with self.rlock:
            if not self.player.is_controlling:
                self.player._is_controlling = True
                self.inform("controls enabled")

    def disable_controls(self):
        with self.rlock:
            if self.player.is_controlling:
                self.player._is_controlling = False
                if self.player.is_connected:
                    self.inform("controls disabled")
                self.reset_controls("player")

    def reset_controls(self, sender):
        assert sender in ["host", "player"]

        with self.rlock:
            if self.callback_executor is not None:
                time = self.time()
                for control in ControlBase._controls:
                    (
                        callbacks,
                        event,
                    ) = control._get_release_callbacks_and_event(sender, time)

                    self.callback_executor.execute_callbacks(
                        callbacks,
                        event.name,
                        self.on_control_finished_callback,
                        event=event,
                    )

    def _state(self):  # name 'state' is reserved by transitions
        return SIMPLIFIED_STATES.get(self.state, self.state)

    def time(self):
        if self.start_time == -1:
            return -1
        else:
            return round(_time() - self.start_time, 2)

    def set_loop(self, loop):
        self.loop = loop
        self.sleep_event_async = asyncio.Event()

    def sleep(self, secs):
        # Triggers even when secs=0
        # (not sure if required here, but at least on sleep_async it is)
        if self.sleep_event_sync.is_set():
            raise SleepCancelledError()

        if self.sleep_event_sync.wait(timeout=secs):
            raise SleepCancelledError()

    async def sleep_async(self, secs):
        assert (
            self.sleep_event_async is not None
        ), "listen() must be called before sleep_async()"

        # Triggers even when secs=0
        if self.sleep_event_async.is_set():
            raise SleepCancelledError()

        try:
            await asyncio.wait_for(
                self.sleep_event_async.wait(),
                timeout=secs,
            )
            raise SleepCancelledError()
        except asyncio.TimeoutError:
            pass


state_machine = ServerStateMachine()

state = State(state_machine)
time = state_machine.time
host = state_machine.host
player = state_machine.player
enable_controls = state_machine.enable_controls
disable_controls = state_machine.disable_controls
sleep = state_machine.sleep
sleep_async = state_machine.sleep_async


def stop():
    try:
        state_machine.stop_immediate()
    except core.MachineError:
        logger.warning(f"Cannot stop() during {state_machine._state()}")
