import asyncio
from collections import OrderedDict

from botafar._internal.callbacks import CallbackBase
from botafar._internal.controls import ControlBase
from botafar._internal.decorators import DecoratorBase
from botafar._internal.events import Event
from botafar._internal.states import state_machine

# HELPERS


def get_cbs(name):
    return CallbackBase.get_by_name(name)


def get_cb(name):
    cbs = get_cbs(name)
    assert len(cbs) == 1
    return cbs[0]


def get_input_cbs(name):
    return ControlBase._get_callbacks(Event(name, "player", "A"))


def get_input_cb(name):
    callbacks = get_input_cbs(name)
    assert len(callbacks) == 1
    return callbacks[0]


def reset():
    CallbackBase._callbacks = {}
    CallbackBase._instances = {}
    DecoratorBase._needs_wrapping = OrderedDict()
    DecoratorBase._wihtout_instance = set()
    DecoratorBase._instance_callbacks = OrderedDict()
    ControlBase._event_callbacks = {}
    ControlBase._controls = []
    state_machine.sleep_event_async = None


def fake_run():
    DecoratorBase.post_listen()

    class MockEvent:
        def is_set(self):
            False

        async def wait(self):
            pass

    state_machine.sleep_event_async = MockEvent()


def get_async_result(func):
    return asyncio.run(func)


def get_cb_result(name, params=[]):
    cb = get_cb(name)
    if asyncio.iscoroutinefunction(cb):
        return get_async_result(cb(*params))
    else:
        return cb(*params)


def get_input_cb_result(name, params=[]):
    cb = get_input_cb(name)
    if asyncio.iscoroutinefunction(cb):
        return get_async_result(cb(*params))
    else:
        return cb(*params)
