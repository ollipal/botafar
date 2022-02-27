import asyncio

from ..callbacks import CallbackBase
from ..constants import (
    LISTEN_MESSAGE,
    LISTEN_WEB_MESSAGE,
    SIGINT_MESSAGE,
    SYSTEM_EVENT,
)
from ..inputs import InputBase
from ..listeners import EnterListener
from ..log_formatter import get_logger, setup_logging
from ..string_utils import error_to_string
from ..websocket import Server
from .telebotties_base import TelebottiesBase

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self):
        super().__init__()
        self.should_connect_keyboard = True
        self.enter_listener = EnterListener()
        self.server = Server(self.event_handler)

    def event_handler(self, event):
        try:
            if event._type == SYSTEM_EVENT:
                self.handle_system_event(event)
                callbacks = CallbackBase._get_callbacks(event)
                self.callback_executor.execute_callbacks(
                    callbacks
                )  # TODO give time if needed?
            else:  # INPUT_EVENT
                callbacks = InputBase._get_callbacks(event)
                self.callback_executor.execute_callbacks(
                    callbacks, event=event
                )
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            self.server.stop()
            self.enter_listener.stop()
            self.should_connect_keyboard = False

    def handle_system_event(self, event):
        if event.name == "connect":
            self.enter_listener.stop()
            print(LISTEN_WEB_MESSAGE)
            self.should_connect_keyboard = False
            logger.info(f"{event.value} connected")

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

    def esc_callback(self):
        pass

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
