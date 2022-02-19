import asyncio

from .log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from .websocket import Client

logger = get_logger()


class Cli(TelebottiesBase):
    def __init__(self):
        self.client = None
        super().__init__()

    def _done(self, future):
        super()._done(future)

        if future.result() is False:  # Send failed
            logger.info("disconnected")
            if self.keyboard_listener.running:
                self.keyboard_listener.stop()

    def process_input(self, key, sender, origin, name):
        future = asyncio.run_coroutine_threadsafe(
            self.client.send(key, sender, origin, name),
            self.loop
        )
        self.register_future(future)

    async def main(self):
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
        success = await self.client.send("A", "player", "keyboard", "connect")
        if not success:
            await self.client.stop()
            return

        try:
            await self.keyboard_listener.run_until_finished()
        finally:
            await self.client.stop()

    def sigint_callback(self):
        asyncio.run_coroutine_threadsafe(self._stop_listener(), self.loop)


def _cli():
    setup_logging("DEBUG")
    Cli().run()
