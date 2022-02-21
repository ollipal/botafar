import asyncio
import concurrent.futures

from ..constants import (
    LISTEN_MESSAGE,
    LISTEN_WEB_MESSAGE,
    SIGINT_MESSAGE,
    SYSTEM_EVENT,
)
from ..inputs import InputBase
from ..listeners import EnterListener
from ..log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from ..websocket import Server
from ..string_utils import error_to_string

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.should_connect_keyboard = True
        self.enter_listener = EnterListener()
        self.server = Server(self.event_handler)

        super().__init__()

    def event_handler(self, event):
        if event._type == SYSTEM_EVENT:
            if event.name == "connect":
                self.enter_listener.stop()
                print(LISTEN_WEB_MESSAGE)
                self.should_connect_keyboard = False
                logger.info(f"{event.value} connected")
            return

        event._update(True, -1)  # TODO properly

        if event._callback_key not in InputBase._event_callbacks:
            return

        callbacks = InputBase._event_callbacks[
            event._callback_key
        ]._get_callbacks_with_parameters(event)

        if callbacks is None:
            return

        # Set callbacks to execute soon (non-blocking)
        for callback, takes_event in callbacks:
            if asyncio.iscoroutinefunction(callback):
                params = [event] if takes_event else []
                future = asyncio.run_coroutine_threadsafe(
                    callback(*params), self.loop
                )
            else:
                params = [callback, event] if takes_event else [callback]
                future = self.executor.submit(*params)
            self.register_future(future)

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

    def sigint_callback(self):
        print(SIGINT_MESSAGE)
        self.server.stop()
        self.enter_listener.stop()
        self.should_connect_keyboard = False


def listen():
    setup_logging("DEBUG")
    Main().run()
