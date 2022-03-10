import asyncio

from ..callback_executor import CallbackExecutor
from ..constants import LISTEN_MESSAGE, LISTEN_WEB_MESSAGE, SIGINT_MESSAGE
from ..listeners import EnterListener
from ..log_formatter import get_logger, setup_logging
from ..states import ServerState
from ..string_utils import error_to_string
from ..websocket import Server
from .telebotties_base import TelebottiesBase

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self):
        self.callback_executor = CallbackExecutor(
            self.done_callback, self.error_callback
        )
        self.state = ServerState(
            self.send_event,
            self.callback_executor.execute_callbacks,
            self.on_remote_client_connect,
        )
        super().__init__()
        self.should_connect_keyboard = True
        self.enter_listener = EnterListener()
        self.server = Server(self.state.process_event)
        self.callback_executor.add_to_takes_event(self._send_event_async)

    def send_event(self, event):
        self.callback_executor.execute_callbacks(
            [self._send_event_async], event=event
        )

    async def _send_event_async(self, event):
        await self.server.send(event)

    def on_remote_client_connect(self):
        if self.enter_listener.running:
            self.enter_listener.stop()
            print(LISTEN_WEB_MESSAGE)
            self.should_connect_keyboard = False

    async def main(self):
        try:
            print(LISTEN_MESSAGE, end="")

            await asyncio.gather(
                self.enter_listener.run_until_finished(self.server.stop),
                self.server.serve(8080),
            )

            if self.should_connect_keyboard:
                await self.keyboard_listener.run_until_finished()
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            self.server.stop()
            self.enter_listener.stop()

    def done_callback(self, future):
        pass

    def sigint_callback(self):
        print(SIGINT_MESSAGE)
        self.server.stop()
        self.enter_listener.stop()
        self.should_connect_keyboard = False


def listen():
    setup_logging("DEBUG")
    Main().run()
