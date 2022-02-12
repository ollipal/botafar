import os
import sys
import threading
from contextlib import contextmanager
from platform import system

_is_windows = system().lower() == "windows"

if _is_windows:
    import msvcrt
else:
    import fcntl

# Nonblocking input check, inspiration from:
# http://ballingt.com/_nonblocking-stdin-in-python-3/
@contextmanager
def _nonblocking(stream):
    # Not required on Windows
    if _is_windows:
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
    if _is_windows:
        if not msvcrt.kbhit():
            return None
        return msvcrt.getwch()
    else:
        try:
            return sys.stdin.read(1)
        except IOError:
            return None


def _enter_callback(enter_event):
    global _stop_thread
    with _nonblocking(sys.stdin):
        while True:
            res = _read_char()
            if res == "\n":
                enter_event.set()
                break
            elif _stop_thread:
                break


def _stop_listening_enter():
    global _stop_thread
    global _t
    _stop_thread = True
    _t.join()


def _start_listening_enter():
    enter_event = threading.Event()
    global _t
    _t = threading.Thread(
        target=_enter_callback, daemon=True, args=(enter_event,)
    )
    _t.start()
    return enter_event


_stop_thread = False
_t = None

if __name__ == "__main__":
    import time

    enter_event = _start_listening_enter()
    for _ in range(5):
        time.sleep(1)
        print(enter_event.is_set())
    _stop_listening_enter()
    print("thread killed")
