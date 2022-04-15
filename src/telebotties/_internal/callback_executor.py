import asyncio
import concurrent.futures
from threading import RLock

from .exceptions import SleepCancelledError
from .log_formatter import get_logger

logger = get_logger()


class CallbackExecutor:
    system_callbacks = {}
    takes_event = set()

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

    @property
    def running_names(self):
        return [
            name
            for name in self.running_futures.keys()
            if not name.startswith("_")
        ]

    def execute_callbacks(
        self, callbacks, name, finished_callback, event=None
    ):
        if len(callbacks) == 0:
            if finished_callback is not None:
                finished_callback()
            return

        for callback in callbacks:
            if event is not None and callback in self.takes_event:
                params = [event]
            else:
                params = []

            if asyncio.iscoroutinefunction(callback):

                async def suppressed(*args):
                    try:
                        await callback(*args)
                    except SleepCancelledError:
                        logger.debug("SleepCancelledError suppressed")

                future = asyncio.run_coroutine_threadsafe(
                    suppressed(*params), self.loop
                )
            else:

                def suppressed(*args):
                    try:
                        callback(*args)
                    except SleepCancelledError:
                        logger.debug("SleepCancelledError suppressed")

                future = self.executor.submit(suppressed, *params)

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
        # TODO skip SleepCancelledErrors
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

        if (
            not future.cancelled()
            and future.exception() is not None
            and not isinstance(future.exception(), SleepCancelledError)
        ):
            self.error_callback(future.exception())
        self.done_callback(future)
