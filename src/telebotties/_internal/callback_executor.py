import asyncio
import concurrent.futures

from .log_formatter import get_logger

logger = get_logger()


class CallbackExecutor:
    system_callbacks = {}
    takes_time = set()
    takes_event = set()
    # takes_time and takes_event needs to be different, otherwise
    # time can be passed as event, if it is optional, registered to
    # both kinds of callbacks

    def __init__(self, done_callback, error_callback):
        self.loop = None
        self.done_callback = done_callback
        self.error_callback = error_callback
        self.futures = set()
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def set_loop(self, loop):
        self.loop = loop

    @staticmethod
    def add_to_takes_event(function):
        CallbackExecutor.takes_event.add(function)

    @staticmethod
    def add_to_takes_time(function):
        CallbackExecutor.takes_time.add(function)

    def execute_callbacks(self, callbacks, event=None, time=None):
        for callback in callbacks:
            if event is not None and callback in self.takes_event:
                params = [event]
            elif time is not None and callback in self.takes_time:
                params = [time]
            else:
                params = []

            if asyncio.iscoroutinefunction(callback):
                future = asyncio.run_coroutine_threadsafe(
                    callback(*params), self.loop
                )
            else:
                future = self.executor.submit(callback, *params)

            self.futures.add(future)
            future.add_done_callback(self._done)

        # TODO return "all finished" awaitable

    def _done(self, future):
        self.futures.remove(future)
        if not future.cancelled() and future.exception() is not None:
            self.error_callback(future.exception())
        self.done_callback(future)
