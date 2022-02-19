import asyncio
import signal
from abc import ABC, abstractmethod

from .listeners import KeyboardListener
from .log_formatter import get_logger
from .string_utils import error_to_string

logger = get_logger()


class TelebottiesBase(ABC):
    def __init__(self, suppress_keys=False):
        self.loop = None
        self.keyboard_listener = KeyboardListener(
            self.process_input, suppress_keys
        )
        self.futures = set()
        self.register_sigint_handler()

    async def _stop_listener(self):
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
        else:
            logger.debug("KeyboardListener was not running")

    def _done(self, future):
        self.futures.remove(future)
        if not future.cancelled() and future.exception() is not None:
            if self.keyboard_listener.running:
                e = future.exception()
                logger.error(error_to_string(e))
                asyncio.run_coroutine_threadsafe(
                    self._stop_listener(), self.loop
                )

    @abstractmethod
    def process_input(self, key, sender, origin, name):
        pass

    async def _main(self):
        self.loop = asyncio.get_running_loop()
        await self.main()

    @abstractmethod
    async def main(self):
        pass

    @abstractmethod
    def sigint_callback(self):
        pass

    def register_future(self, future):
        self.futures.add(future)
        future.add_done_callback(self._done)

    def register_sigint_handler(self):
        original_sigint_handler = signal.getsignal(signal.SIGINT)

        def signal_handler(_signal, frame):
            signal.signal(signal.SIGINT, original_sigint_handler)  # Reset
            self.sigint_callback()
            asyncio.run_coroutine_threadsafe(self._stop_listener(), self.loop)

        signal.signal(signal.SIGINT, signal_handler)

    def run(self):
        asyncio.run(self._main())