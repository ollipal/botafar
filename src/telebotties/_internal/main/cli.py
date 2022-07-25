import asyncio
import sys

import click

from ... import __version__
from ..callback_executor import CallbackExecutor
from ..constants import SYSTEM_EVENT
from ..log_formatter import get_logger, setup_logging
from ..states import KeyboardClientState
from ..string_utils import error_to_string
from ..websocket import Client
from .telebotties_base import TelebottiesBase

logger = get_logger()


class Cli(TelebottiesBase):
    def __init__(self, address, suppress_keys, prints_removed):
        assert isinstance(address, str), f"Invalid address {address}"
        assert len(address.split(":")) == 2, f"Invalid address {address}"

        self.prints_removed = prints_removed
        self.callback_executor = CallbackExecutor(
            self.done_callback, self._error_callback
        )
        self.event_prosessor = KeyboardClientState(
            self.send_event, self.end_callback
        )
        super().__init__(suppress_keys, prints_removed)
        self.client = Client(address, self.event_prosessor.process_event)
        self.callback_executor.add_to_takes_event(self._send_event_async)

    def send_event(self, event):
        self.callback_executor.execute_callbacks(
            [self._send_event_async], "_send_event", None, event=event
        )

    async def _send_event_async(self, event):
        send_success = await self.client.send(event)
        if not send_success or (
            event._type == SYSTEM_EVENT and event.name == "host_disconnect"
        ):
            if event._type == SYSTEM_EVENT and event.name == "host_disconnect":
                logger.debug("client_disconnect detected")
            return False

    async def main(self):
        try:
            try:
                control_datas = await self.client.connect()
            except ConnectionRefusedError:
                if not self.prints_removed:
                    print(
                        f"Connection refused to {self.client.address}, "
                        "wrong address or bot not running?"
                    )
                return
            except RuntimeError:
                if not self.prints_removed:
                    print(
                        f"Connection refused to {self.client.address}, "
                        "other host already connected"
                    )
                return

            task = asyncio.create_task(self.client.receive())
            await self.keyboard_listener.run_until_finished(
                control_datas, False
            )
            await self.client.stop()
            await task
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            self.keyboard_listener.stop()
            if self.client is not None:
                await self.client.stop()

    def end_callback(self):
        self.keyboard_listener.stop()

    def error_callback(self, e):
        pass

    def done_callback(self, future):
        if future.result() is False:  # Send failed or Esc pressed
            logger.debug("Keyboard disconnected")
            self.keyboard_listener.stop()

    def sigint_callback(self):
        pass


@click.command(
    help="telebotties cli, use --connect to control running bots.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "-c",
    "--connect",
    is_flag=False,
    metavar="",
    flag_value="127.0.0.1:1996",
    default=None,
    help="Connect keyboard to address, default: 127.0.0.1:1996.",
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
@click.option(
    "-v", "--version", is_flag=True, help="Prints telebotties version."
)
def _cli(connect, log_level, no_help, version):
    suppress_keys = True

    # Show help if no args empty
    if len(sys.argv) == 1:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if version:
        click.echo(__version__)
        return

    # Keep this import here, required for Cli, but errors silenced
    # in keyboard_listener.py, because normal bots can be used without
    from pynput import keyboard  # noqa: F401

    setup_logging(log_level.upper())
    Cli(connect, suppress_keys, no_help).run()
