import asyncio
import signal
from abc import ABC, abstractmethod

import nest_asyncio

from ..log_formatter import get_logger

logger = get_logger()


class BotafarBase(ABC):
    def __init__(self, suppress_keys, prints_removed):
        assert self.callback_executor is not None
        assert self.event_prosessor is not None
        assert self.event_prosessor.process_event is not None

        self.register_sigint_handler()
        self.loop = None

    def _error_callback(self, e):
        self.error_callback(e)

    async def _main(self):
        self.loop = asyncio.get_running_loop()
        self.callback_executor.set_loop(self.loop)
        await self.main()

    @abstractmethod
    def send_event(self, event):
        pass

    @abstractmethod
    async def main(self):
        pass

    @abstractmethod
    def done_callback(self, future):
        pass

    @abstractmethod
    def error_callback(self, e):
        pass

    @abstractmethod
    def sigint_callback(self):
        pass

    def register_sigint_handler(self):
        original_sigint_handler = signal.getsignal(signal.SIGINT)

        def signal_handler(_signal, frame):
            signal.signal(signal.SIGINT, original_sigint_handler)  # Reset
            self.sigint_callback()

        signal.signal(signal.SIGINT, signal_handler)

    def run(self):
        nest_asyncio.apply()  # Allows calling run() inside a running loop
        asyncio.run(self._main())
