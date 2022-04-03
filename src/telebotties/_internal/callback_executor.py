import asyncio
import concurrent.futures
from threading import RLock

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
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.future_to_name = {}
        self.running_futures = {}
        self.finished_callbacks = {}  # bad name... callback when finished
        self.rlock = RLock()  # Make sure future tracking stays in sync

    def set_loop(self, loop):
        self.loop = loop

    @staticmethod
    def add_to_takes_event(function):
        CallbackExecutor.takes_event.add(function)

    @staticmethod
    def add_to_takes_time(function):
        CallbackExecutor.takes_time.add(function)

    @property
    def running_names(self):
        return [
            name
            for name in self.running_futures.keys()
            if not name.startswith("_")
        ]

    def execute_callbacks(
        self, callbacks, name, finished_callback, event=None, time=None
    ):
        if len(callbacks) == 0:
            finished_callback()
            return

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

            with self.rlock:
                if finished_callback is not None:
                    # NOTE this can override existing, which should be ok
                    self.finished_callbacks[name] = finished_callback
                self.future_to_name[future] = name
                if name not in self.running_futures:
                    self.running_futures[name] = set()
                self.running_futures[name].add(future)

            # TODO can future finish before done callback is added?
            # Probably just then triggers immediately
            future.add_done_callback(self._done)

    async def wait_until_finished(self, name):
        futures = self.running_futures.get(name, [])
        await asyncio.gather(*[asyncio.wrap_future(f) for f in futures])

    async def wait_until_all_finished(self):
        futures = set().union(*self.running_futures.values())
        await asyncio.gather(*[asyncio.wrap_future(f) for f in futures])

    def _done(self, future):
        with self.rlock:
            name = self.future_to_name[future]
            del self.future_to_name[future]

            self.running_futures[name].remove(future)
            if len(self.running_futures[name]) == 0:
                del self.running_futures[name]

                callback = self.finished_callbacks.pop(name, None)
                if callback is not None:
                    callback()

        if not future.cancelled() and future.exception() is not None:
            self.error_callback(future.exception())
        self.done_callback(future)
