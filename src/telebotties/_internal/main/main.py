import asyncio

import click

from telebotties._internal.events.system_event import SystemEvent
from telebotties._internal.inputs.input_base import InputBase
from telebotties._internal.ip_addr import get_ip

from ..callback_executor import CallbackExecutor
from ..constants import (
    LISTEN_WEB_MESSAGE_NO_PYNPUT,
    LISTEN_WEB_MESSAGE_PYNPUT,
    SIGINT_MESSAGE,
)
from ..listeners import EnterListener, pynput_supported
from ..log_formatter import get_logger, setup_logging
from ..states import ServerState
from ..string_utils import error_to_string, get_welcome_message
from ..websocket import Server
from .telebotties_base import TelebottiesBase

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self, port, suppress_keys, prints_removed):
        self.prints_removed = prints_removed
        self.callback_executor = CallbackExecutor(
            self.done_callback, self._error_callback
        )
        self.state = ServerState(
            self.send_event,
            self.callback_executor.execute_callbacks,
            self.on_remote_client_connect,
        )
        super().__init__(suppress_keys, prints_removed)
        self.port = port
        self.should_connect_keyboard = True
        self.enter_listener = EnterListener()
        self.server = Server(self.state.process_event)
        self.callback_executor.add_to_takes_event(self._send_event_async)
        self.non_pynput_help_printed = False

    def send_event(self, event):
        if self.server.connected:
            self.callback_executor.execute_callbacks(
                [self._send_event_async], event=event
            )
        else:
            logger.debug("server was not connected, not sending")

    async def _send_event_async(self, event):
        await self.server.send(event)

    def on_remote_client_connect(self):
        if self.enter_listener.running:
            self.enter_listener.stop()
            if not self.prints_removed:
                print(LISTEN_WEB_MESSAGE_PYNPUT)

        if not pynput_supported and not self.non_pynput_help_printed:
            if not self.prints_removed:
                print(LISTEN_WEB_MESSAGE_NO_PYNPUT)
                self.non_pynput_help_printed = True

        self.should_connect_keyboard = False

    async def main(self):
        try:

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
                await self.keyboard_listener.run_until_finished(
                    InputBase._get_input_datas(), True
                )
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            self.server.stop()
            self.enter_listener.stop()

    def error_callback(self, e, sigint=False):
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

        if self.server.connected:
            self.send_event(
                SystemEvent(
                    "client_disconnect",
                    "server",
                )
            )
        else:
            self.state.process_event(
                SystemEvent(
                    "client_disconnect",
                    "server",
                )
            )

        # TODO there is no check that send_events have been done

        self.should_connect_keyboard = False
        self.server.stop()
        self.enter_listener.stop()

    def done_callback(self, future):
        pass

    def sigint_callback(self):
        if not self.prints_removed:
            print(SIGINT_MESSAGE)
        self.error_callback(None, sigint=True)


def _main(log_level, port, suppress_keys, prints_removed):
    setup_logging(log_level)
    Main(port, suppress_keys, prints_removed).run()


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
@click.option(
    "-s",
    "--suppress-keys",
    is_flag=True,
    help="Suppress key events from other programs.",
)
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
def _cli(port, suppress_keys, log_level, no_help):
    _main(log_level.upper(), port, suppress_keys, no_help)


def listen(cli_enabled=True):
    if cli_enabled:
        _cli()
    else:
        _main("INFO", 1996, False, False)
