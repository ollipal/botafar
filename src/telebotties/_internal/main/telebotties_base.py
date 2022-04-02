import asyncio
import signal
from abc import ABC, abstractmethod

from ..listeners import KeyboardListener
from ..log_formatter import get_logger

logger = get_logger()


class TelebottiesBase(ABC):
    def __init__(self, suppress_keys, prints_removed):
        assert self.callback_executor is not None
        assert self.event_prosessor is not None
        assert self.event_prosessor.process_event is not None

        self.keyboard_listener = KeyboardListener(
            self.event_prosessor.process_event, suppress_keys, prints_removed
        )
        self.register_sigint_handler()
        self.loop = None

    def _error_callback(self, e):
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
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
            self.keyboard_listener.stop()

        signal.signal(signal.SIGINT, signal_handler)

    def run(self):
        asyncio.run(self._main())
