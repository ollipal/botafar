import os
import sys
import threading
from contextlib import contextmanager
from platform import system

is_windows = system().lower() == "windows"

if is_windows:
    import msvcrt
else:
    import fcntl


# Nonblocking input check, inspiration from:
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


def _enter_callback(enter_event):
    global stop_thread
    with _nonblocking(sys.stdin):
        while True:
            res = _read_char()
            if res == "\n":
                enter_event.set()
                break
            elif stop_thread:
                break


def stop_listening_enter():
    global stop_thread
    global t
    stop_thread = True
    t.join()


def start_listening_enter():
    enter_event = threading.Event()
    global t
    t = threading.Thread(
        target=_enter_callback, daemon=True, args=(enter_event,)
    )
    t.start()
    return enter_event


stop_thread = False
t = None

if __name__ == "__main__":
    import time

    enter_event = start_listening_enter()
    for _ in range(5):
        time.sleep(1)
        print(enter_event.is_set())
    stop_listening_enter()
    print("thread killed")
