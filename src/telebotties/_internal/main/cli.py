import asyncio

from ..events import SystemEvent
from ..log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from ..websocket import Client
from ..string_utils import error_to_string

logger = get_logger()


class Cli(TelebottiesBase):
    def __init__(self):
        self.client = None
        super().__init__()

    def _done(self, future):
        super()._done(future)

        if future.result() is False:  # Send failed
            logger.info("Keyboard disconnected")
            if self.keyboard_listener.running:
                self.keyboard_listener.stop()

    def event_handler(self, event):
        event._update(True, -1)
        future = asyncio.run_coroutine_threadsafe(
            self.client.send(event), self.loop
        )
        self.register_future(future)

    async def main(self):
        try:
            self.client = Client(8080)

            try:
                await self.client.connect()
            except ConnectionRefusedError:
                print(
                    "Connection refused to 127.0.0.1:8080, "
                    "wrong address or bot not running?"
                )
                return

            # Check even first send, it does not raise errors
            # (they do not seem to work as expected)
            connect_event = SystemEvent("connect", "player", "", None)
            success = await self.client.send(connect_event)
            if not success:
                await self.client.stop()
                return

            await self.keyboard_listener.run_until_finished()
            await self.client.stop()
        except Exception as e:
            logger.error(f"Unexpected internal error: {error_to_string(e)}")
            if self.keyboard_listener.running:
                self.keyboard_listener.stop()
            if self.client is not None:
                await self.client.stop()


    def sigint_callback(self):
        pass


def _cli():
    setup_logging("DEBUG")
    Cli().run()
