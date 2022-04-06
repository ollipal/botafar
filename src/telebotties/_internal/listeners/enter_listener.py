import asyncio
import os
import sys
import threading
from contextlib import contextmanager
from platform import system

from ..log_formatter import get_logger

is_windows = system().lower() == "windows"

if is_windows:
    import msvcrt
else:
    import fcntl

logger = get_logger()


# Nonblocking control check, inspiration from:
# http://ballingt.com/_nonblocking-stdin-in-python-3/
@contextmanager
def _nonblocking(stream):
    # Not required on Windows
    if is_windows:
        yield
        return

    fd = stream.fileno()
    orig_fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        fcntl.fcntl(fd, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        yield
    finally:
        fcntl.fcntl(fd, fcntl.F_SETFL, orig_fl)


def _read_char():
    if is_windows:
        if not msvcrt.kbhit():
            return None
        return msvcrt.getwch()
    else:
        try:
            return sys.stdin.read(1)
        except IOError:
            return None


class EnterListener:
    def __init__(self):
        self._running = False
        self._thread = None

    async def run_until_finished(self, enter_callback):
        if self.running:
            logger.debug("EnterListener was already running")
            return

        self._running = True
        self._event = asyncio.Event()
        self._loop = asyncio.get_running_loop()

        self._thread = threading.Thread(
            target=self._char_checker,
            daemon=True,
            args=(
                self._event,
                enter_callback,
            ),
        )
        self._thread.start()
        await self._event.wait()
        self._thread.join()

    def stop(self):
        if not self.running:
            logger.debug("EnterListener was not running")
            return

        self._running = False
        self._loop.call_soon_threadsafe(self._event.set)

    @property
    def running(self):
        return self._running

    def _char_checker(self, event, enter_callback):
        with _nonblocking(sys.stdin):
            while True:
                res = _read_char()
                if res == "\n":
                    enter_callback()
                    self.stop()
                    break
                elif not self.running:
                    break


if __name__ == "__main__":

    def enter():
        print("Enter")

    enter_listener = EnterListener()

    async def stop_in_5():
        await asyncio.sleep(5)
        enter_listener.stop()

    async def main():
        await enter_listener.run_until_finished(enter)

        # await asyncio.gather(
        #    enter_listener.run_until_finished(enter),
        #    stop_in_5()
        # )

        print("thread killed")

    asyncio.run(main())
