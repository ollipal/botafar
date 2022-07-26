import asyncio

import click

from telebotties._internal.callbacks.callback_base import CallbackBase
from telebotties._internal.controls.control_base import ControlBase
from telebotties._internal.events.system_event import SystemEvent
from telebotties._internal.ip_addr import get_ip

from ..callback_executor import CallbackExecutor
from ..constants import (
    LISTEN_WEB_MESSAGE_NO_PYNPUT,
    LISTEN_WEB_MESSAGE_PYNPUT,
    SIGINT_MESSAGE,
)
from ..decorators import DecoratorBase
from ..listeners import EnterListener, pynput_supported
from ..log_formatter import get_logger, setup_logging
from ..states import PRE_INIT, ServerEventProsessor, state_machine
from ..string_utils import error_to_string, get_welcome_message
from ..websocket import Server
from .telebotties_base import TelebottiesBase

logger = get_logger()
main = None


class Main(TelebottiesBase):
    def __init__(self, port, suppress_keys, prints_removed):
        self.prints_removed = prints_removed
        self.callback_executor = CallbackExecutor(
            self.done_callback, self._error_callback
        )
        self.event_prosessor = ServerEventProsessor(
            self.send_event,
            self.callback_executor,
            self.on_remote_host_connect,
        )
        super().__init__(suppress_keys, prints_removed)
        self.port = port
        self.should_connect_keyboard = True
        self.enter_listener = EnterListener()
        self.server = Server(self.event_prosessor.process_event)
        self.callback_executor.add_to_takes_event(self._send_event_async)
        self.non_pynput_help_printed = False

    def send_event(self, event):
        if self.server.connected:
            self.callback_executor.execute_callbacks(
                [self._send_event_async], "_send_event", None, event=event
            )
        else:
            logger.debug("server was not connected, not sending")

    async def _send_event_async(self, event):
        await self.server.send(event)

    def print(self, string):
        if self.server.connected:
            self.send_event(
                SystemEvent(
                    "print",
                    string,
                )
            )
        else:
            # logger.debug("Server not connected, print not sent")
            pass

    def on_remote_host_connect(self):
        if self.enter_listener.running:
            self.enter_listener.stop()
            if not self.prints_removed:
                print(LISTEN_WEB_MESSAGE_PYNPUT)

        if not pynput_supported and not self.non_pynput_help_printed:
            if not self.prints_removed:
                print(LISTEN_WEB_MESSAGE_NO_PYNPUT)
                self.non_pynput_help_printed = True

        self.should_connect_keyboard = False

    async def run_callbacks(self, name, callback):
        self.callback_executor.execute_callbacks(
            CallbackBase.get_by_name(name), name, callback
        )
        await self.callback_executor.wait_until_finished(name)
        # Await also all internal callbacks, such as _send
        await self.callback_executor.wait_until_all_finished()

    async def main(self):
        DecoratorBase.post_listen()
        state_machine.set_loop(self.loop)
        try:
            state_machine.init()
            await self.run_callbacks("on_init", state_machine.wait_host)

            if state_machine._state() == "on_exit":
                return  # triggers 'finally:'

            ip = get_ip()  # TODO save
            if not self.prints_removed:
                print(
                    get_welcome_message(ip, self.port, pynput_supported),
                    end="",
                )

            if pynput_supported:
                await asyncio.gather(
                    self.enter_listener.run_until_finished(self.server.stop),
                    self.server.serve(self.port),
                )
            else:
                await self.server.serve(self.port)

            if pynput_supported and self.should_connect_keyboard:
                self.event_prosessor.set_to_local()
                await self.keyboard_listener.run_until_finished(
                    ControlBase._get_control_datas(), True
                )
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            await self.server.stop_async()
            self.enter_listener.stop()
        finally:
            state_machine.exit_immediate()
            await state_machine.wait_exit()
            # This is probably unnecessary but let's keep it for now
            await self.callback_executor.wait_until_all_finished()

    def error_callback(self, e, sigint=False, exit=False):
        if e is not None:
            logger.error(error_to_string(e))

            if self.server.connected:
                self.send_event(
                    SystemEvent(
                        "error",
                        f"bot crashed: {type(e).__name__}",
                        text=error_to_string(e),
                    )
                )

        if sigint and self.server.connected:
            self.send_event(
                SystemEvent("info", None, text="bot received Ctrl + C")
            )

        if exit and self.server.connected:
            self.send_event(
                SystemEvent("info", None, text="bot .exit() called")
            )

        if self.server.connected:
            self.send_event(
                SystemEvent(
                    "host_disconnect",
                    "server",
                )
            )
        else:
            pass  # Does not continue locally

        self.should_connect_keyboard = False
        self.server.stop()
        self.enter_listener.stop()

    def exit(self):
        state_machine.exit_immediate()
        self.error_callback(None, exit=True)
        self.keyboard_listener.stop()

    def done_callback(self, future):
        pass

    def sigint_callback(self):
        if not self.prints_removed:
            print(SIGINT_MESSAGE)
        state_machine.exit_immediate()
        self.error_callback(None, sigint=True)
        self.keyboard_listener.stop()


def _print(string, print_locally=True):
    global main
    string = str(string)
    if main is not None:
        main.print(string)
    if print_locally:
        print(string)


def exit():
    global main
    if main is not None:
        main.exit()
    else:
        raise RuntimeError("tb.exit() cannot be called before tb.run()")


def _main(log_level, port, suppress_keys, prints_removed):
    assert state_machine.state == PRE_INIT, "tb.run() can be called only once"
    global main
    setup_logging(log_level)
    main = Main(port, suppress_keys, prints_removed)
    main.run()


@click.command(
    help="telebotties bot cli",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "-p",
    "--port",
    is_flag=False,
    metavar="",
    flag_value="1996",
    default="1996",
    help="Telebotties listening port, default: 1996",
)
# @click.option(
#    "-s",
#    "--suppress-keys",
#    is_flag=True,
#    help="Suppress key events from other programs.",
# )
@click.option(
    "-l",
    "--log-level",
    metavar="",
    type=click.Choice(
        ["debug", "info", "warning", "error"], case_sensitive=False
    ),
    help="Log level: debug|info|warning|error, default: info.",
    default="info",
)  # level 'critical' is not in use currently
@click.option(
    "-n",
    "--no-help",
    is_flag=True,
    help="Removes help messages from standard out.",
)
def _cli(port, log_level, no_help):
    suppress_keys = True
    _main(log_level.upper(), port, suppress_keys, no_help)


def run(cli=True):
    if cli:
        _cli.main(
            standalone_mode=False
        )  # Why not just _cli(): https://stackoverflow.com/a/60321370/7388328
    else:
        _main("INFO", 1996, False, False)
