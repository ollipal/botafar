import asyncio
import signal
from abc import ABC, abstractmethod

from .log_formatter import get_logger
from .string_utils import error_to_string

logger = get_logger()


class TelebottiesBase(ABC):
    def __init__(self):
        self.loop = None  # Will be set in _main
        self.listener = None
        self.futures = set()
        self.register_sigint_handler()

    async def _stop_listener(self):
        if self.listener is not None:
            self.listener.wait()
            self.listener.stop()
        else:
            logger.debug("listener was None")

    def _done(self, future):
        self.futures.remove(future)
        if not future.cancelled() and future.exception() is not None:
            if self.listener.running:
                e = future.exception()
                logger.error(error_to_string(e))
                asyncio.run_coroutine_threadsafe(
                    self._stop_listener(), self.loop
                )

    @abstractmethod
    def process_input(self, key, sender, origin, name):
        pass

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
        asyncio.run(self.main())
