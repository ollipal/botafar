import asyncio

import click

from botafar._internal.callbacks.callback_base import CallbackBase
from botafar._internal.events.system_event import SystemEvent

from ..callback_executor import CallbackExecutor
from ..constants import LISTEN_BROWSER_MESSAGE, SIGINT_MESSAGE
from ..data_channel import DataChannel
from ..decorators import DecoratorBase
from ..log_formatter import get_logger, setup_logging
from ..states import PRE_INIT, ServerEventProsessor, state_machine
from ..string_utils import error_to_string, get_welcome_message
from .botafar_base import BotafarBase

logger = get_logger()
main = None


class Main(BotafarBase):
    def __init__(self, suppress_keys, prints_removed):
        self.prints_removed = prints_removed
        self.callback_executor = CallbackExecutor(
            self.done_callback, self._error_callback
        )
        self.event_prosessor = ServerEventProsessor(
            self.send_event,
            self.callback_executor,
            self.on_initial_browser_connect,
        )
        super().__init__(suppress_keys, prints_removed)
        self.server = DataChannel(self.event_prosessor.process_event)
        self.callback_executor.add_to_takes_event(self._send_event_async)
        self.timeout_task = None

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

    def on_initial_browser_connect(self):
        if not self.prints_removed:
            print(LISTEN_BROWSER_MESSAGE)

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
            await self.run_callbacks("on_init", state_machine.wait_browser)

            if state_machine._state() == "on_exit":
                return  # triggers 'finally:'

            if not self.prints_removed:
                print(
                    get_welcome_message(self.server.id),
                    end="",
                    flush=True,
                )

            async def timeout(t):
                try:
                    await asyncio.sleep(t)
                    if not self.server.has_connected:
                        if not self.prints_removed:
                            print(
                                f"\nDid not connect in {t} seconds. "
                                "Did you try to open the link above?\n"
                            )
                        self.server.stop()
                except asyncio.CancelledError:
                    logger.debug("Timeout cancelled")

            async def serve():
                await self.server.serve()
                if self.timeout_task is not None:
                    self.timeout_task.cancel()

            self.timeout_task = asyncio.create_task(timeout(60))
            self.server_task = asyncio.create_task(serve())

            await asyncio.gather(
                self.timeout_task,
                self.server_task,
            )
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
        finally:
            if self.timeout_task is not None:
                self.timeout_task.cancel()
            await self.server.stop_async()
            state_machine.exit_immediate()
            await state_machine.wait_exit()
            # This is probably unnecessary but let's keep it for now
            await self.callback_executor.wait_until_all_finished()

    def error_callback(self, e, sigint=False, exit=False):
        if self.timeout_task is not None:
            self.timeout_task.cancel()

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
                    "owner_disconnect",
                    "server",
                )
            )
        else:
            pass  # Does not continue locally

        self.should_connect_keyboard = False
        self.server.stop()

    def exit(self):
        state_machine.exit_immediate()
        self.error_callback(None, exit=True)

    def done_callback(self, future):
        pass

    def sigint_callback(self):
        if not self.prints_removed:
            print(SIGINT_MESSAGE)
        state_machine.exit_immediate()
        self.error_callback(None, sigint=True)


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
        raise RuntimeError(
            "botafar.exit() cannot be called before botafar.run()"
        )


def _main(log_level, suppress_keys, prints_removed):
    assert (
        state_machine.state == PRE_INIT
    ), "botafar.run() can be called only once"
    global main
    setup_logging(log_level)
    main = Main(suppress_keys, prints_removed)
    main.run()


@click.command(
    help="botafar bot cli",
    context_settings=dict(help_option_names=["-h", "--help"]),
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
    help="Log level: debug / info / warning / error, default: info.",
    default="info",
)  # level 'critical' is not in use currently
@click.option(
    "-n",
    "--no-help",
    is_flag=True,
    help="Removes help messages from standard out.",
)
def _cli(log_level, no_help):
    suppress_keys = True
    _main(log_level.upper(), suppress_keys, no_help)


def run(cli=True):
    if cli:
        _cli.main(
            standalone_mode=False
        )  # Why not just _cli(): https://stackoverflow.com/a/60321370/7388328
    else:
        _main("INFO", 1996, False, False)
