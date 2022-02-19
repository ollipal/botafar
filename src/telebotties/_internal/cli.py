import asyncio

from .constants import LISTEN_KEYBOARD_MESSAGE
from .listeners import listen_keyboard_wrapper
from .log_formatter import get_logger, setup_logging
from .telebotties_base import TelebottiesBase
from .websocket import Client

logger = get_logger()


class Cli(TelebottiesBase):
    def __init__(self):
        self.client = None
        super().__init__()

    def process_input(self, key, sender, origin, name):
        future = self.loop.create_task(
            self.client.send(key, sender, origin, name)
        )
        self.register_future(future)

    async def main(self):
        self.loop = asyncio.get_running_loop()
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
        res = await self.client.send("A", "player", "keyboard", "connect")
        if not res:
            await self.client.stop()
            return

        print(LISTEN_KEYBOARD_MESSAGE)

        listen_keyboard_non_blocking = listen_keyboard_wrapper(
            self.process_input
        )
        self.listener = listen_keyboard_non_blocking()

        try:
            while self.listener.running:
                await asyncio.sleep(0.1)
        finally:
            await self.client.stop()
            print()

        await asyncio.sleep(2)

    def sigint_callback(self):
        asyncio.run_coroutine_threadsafe(self._stop_listener(), self.loop)


def _cli():
    setup_logging("DEBUG")
    tb_cli = Cli()
    tb_cli.run()
