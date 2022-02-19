import asyncio
import concurrent.futures

from .constants import (
    LISTEN_KEYBOARD_MESSAGE,
    LISTEN_MESSAGE,
    LISTEN_WEB_MESSAGE,
    SIGINT_MESSAGE,
)
from .inputs import Event, InputBase
from .listeners import (
    listen_keyboard_wrapper,
    start_listening_enter,
    stop_listening_enter,
)
from .log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from .websocket import Server

logger = get_logger()


class Main(TelebottiesBase):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.server = None
        self.connected = False
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
        self.loop = asyncio.get_running_loop()

        print(LISTEN_MESSAGE, end="")

        def event_handler(event):
            if "connect" in event:
                stop_listening_enter()
                print(LISTEN_WEB_MESSAGE)
                self.connected = True
            print(f"event={event}")

        self.server = Server(event_handler)

        enter_event = start_listening_enter()

        async def wait_enter():
            while not self.connected:
                if enter_event.is_set():
                    self.server.stop()
                    break
                await asyncio.sleep(0.1)

        await asyncio.gather(
            self.server.serve(8080),
            wait_enter(),
        )

        if not self.connected:
            print(LISTEN_KEYBOARD_MESSAGE)

            listen_keyboard_non_blocking = listen_keyboard_wrapper(
                self.process_input
            )
            self.listener = listen_keyboard_non_blocking()

            try:
                # asyncio.Event() would be cleaner if can get to work
                while self.listener.running:
                    await asyncio.sleep(0.1)
            finally:
                print()

        await asyncio.sleep(2)

    def sigint_callback(self):
        print(SIGINT_MESSAGE)
        self.server.stop()
        stop_listening_enter()  # Not sure if this ok
        self.connected = True  # TODO better way


def listen():
    setup_logging("DEBUG")
    tb_main = Main()
    tb_main.run()
