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
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.future_to_name = {}
        self.running_futures = {}
        self.finished_callbacks = {}  # bad name... callback when finished

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

        if finished_callback is not None:
            # NOTE this will override previous, which is ok currently
            self.finished_callbacks[name] = finished_callback

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

            # TODO can future finish before done callback is added?
            self.future_to_name[future] = name
            if name not in self.running_futures:
                self.running_futures[name] = set()
            self.running_futures[name].add(future)
            future.add_done_callback(self._done)

    async def wait_until_finished(self, name):
        futures = self.running_futures.get(name, [])
        await asyncio.gather(*[asyncio.wrap_future(f) for f in futures])

    def _done(self, future):
        name = self.future_to_name.pop(future, None)
        self.running_futures[name].remove(future)
        if len(self.running_futures[name]) == 0:
            removed = self.running_futures.pop(name, None)
            if removed is None:
                # TODO warn non-inputs only?
                logger.warning("None retuned, should not happen!")
            elif (
                len(removed) != 0
            ):  # This triggers, if added between if and pop
                # TODO warn non-inputs only?
                logger.warning("Running callbacks removed, trying fix!")
                self.running_futures[name] = removed

            callback = self.finished_callbacks.pop(name, None)
            if callback is not None:
                callback()

        if not future.cancelled() and future.exception() is not None:
            self.error_callback(future.exception())
        self.done_callback(future)
