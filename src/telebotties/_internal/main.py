import asyncio
import concurrent.futures

from .constants import LISTEN_MESSAGE, LISTEN_WEB_MESSAGE, SIGINT_MESSAGE
from .inputs import Event, InputBase
from .listeners import EnterListener
from .log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from .websocket import Server

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.server = None
        self.connected = False
        self.enter_listener = None
        super().__init__()

    def process_input(self, key, sender, origin, name):
        event_key = (key, sender, origin)
        if event_key not in InputBase._event_callbacks:
            return

        event = Event(name, True, sender, origin, -1)
        callbacks = InputBase._event_callbacks[
            event_key
        ]._get_callbacks_with_parameters(key, event)

        if callbacks is None:
            return

        # Set callbacks to execute soon (non-blocking)
        # TODO check sshkeyboard for more up to date handling?
        for callback, takes_event in callbacks:
            # TODO use param
            if asyncio.iscoroutinefunction(callback):
                if takes_event:
                    future = asyncio.run_coroutine_threadsafe(
                        callback(event), self.loop
                    )
                else:
                    future = asyncio.run_coroutine_threadsafe(
                        callback(), self.loop
                    )
            else:
                if takes_event:
                    future = self.executor.submit(callback, event)
                else:
                    future = self.executor.submit(callback)
            self.register_future(future)

    async def main(self):
        print(LISTEN_MESSAGE, end="")

        self.enter_listener = EnterListener()

        def event_handler(event):
            if "connect" in event:
                if self.enter_listener.running:
                    self.enter_listener.stop()
                print(LISTEN_WEB_MESSAGE)
                self.connected = True
            print(f"event={event}")

        self.server = Server(event_handler)

        await asyncio.gather(
            self.enter_listener.run_until_finished(self.server.stop),
            self.server.serve(8080),
        )

        if not self.connected:
            await self.keyboard_listener.run_until_finished()

    def sigint_callback(self):
        print(SIGINT_MESSAGE)
        self.server.stop()
        if self.enter_listener is not None and self.enter_listener.running:
            self.enter_listener.stop()  # Not sure if this ok
        else:
            logger.debug("enter_listener was None or not running")
        self.connected = True  # TODO better way


def listen():
    setup_logging("DEBUG")
    Main().run()
