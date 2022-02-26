import asyncio
import signal
from abc import ABC, abstractmethod

from ..callback_executor import CallbackExecutor
from ..listeners import KeyboardListener
from ..log_formatter import get_logger
from ..string_utils import error_to_string

logger = get_logger()


class TelebottiesBase(ABC):
    def __init__(self, suppress_keys=False):
        self.keyboard_listener = KeyboardListener(
            self.event_handler, suppress_keys
        )
        self.register_sigint_handler()
        self.callback_executor = CallbackExecutor(
            self.done_callback, self.error_callback
        )
        self.loop = None

    def error_callback(self, e):
        if self.keyboard_listener.running:
            logger.error(error_to_string(e))
            self.keyboard_listener.stop()

    @abstractmethod
    def event_handler(self, event):
        pass

    async def _main(self):
        self.loop = asyncio.get_running_loop()
        self.callback_executor.set_loop(self.loop)
        await self.main()

    @abstractmethod
    async def main(self):
        pass

    @abstractmethod
    def done_callback(self, future):
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