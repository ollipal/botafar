import asyncio

import pytest

from telebotties import on_init
from telebotties._internal.callbacks import CallbackBase
from telebotties._internal.decorators import DecoratorBase

# HELPERS


def get_cb():
    assert len(CallbackBase.get_by_name("on_init")) == 1
    return CallbackBase.get_by_name("on_init")[0]


def reset():
    CallbackBase._callbacks = {}
    DecoratorBase._needs_wrapping = {}
    DecoratorBase._wihtout_instance = set()


def get_async_result(func):
    return asyncio.run(func)


# TESTS


def test_on_init_empty_parenthesis_errors():
    reset()
    with pytest.raises(AssertionError):

        @on_init()
        def example():
            return 3


def test_on_init_extra_kwargs_errors():
    reset()
    with pytest.raises(AssertionError):

        @on_init(a=7)
        def example():
            return 3


def test_on_init_extra_args_errors():
    reset()
    with pytest.raises(AssertionError):

        @on_init(7, 8)
        def example():
            return 3


def test_function():
    reset()

    @on_init
    def example():
        return 3

    DecoratorBase._wrap_ones_without_wrapping()
    assert example() == 3
    assert get_cb()() == 3


def test_function_async():
    reset()

    @on_init
    async def example():
        return 3

    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(example()) == 3
    assert get_async_result(get_cb()()) == 3


def test_lambda():
    reset()
    on_init(lambda: 3)
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_cb()() == 3


def test_class_instance():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        def example(self):
            return self.val + 2

    c = Class()

    on_init(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert c.example() == 3
    assert get_cb()() == 3


def test_class_instance_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        async def example(self):
            return self.val + 2

    c = Class()

    on_init(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(c.example()) == 3
    assert get_async_result(get_cb()()) == 3


def test_class_instance_static():
    reset()

    class Class:
        @staticmethod
        def example():
            return 3

    c = Class()

    on_init(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert c.example() == 3
    assert get_cb()() == 3


def test_class_instance_static_async():
    reset()

    class Class:
        @staticmethod
        async def example():
            return 3

    c = Class()

    on_init(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(c.example()) == 3
    assert get_async_result(get_cb()()) == 3


def test_class_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_init
        def example(self):
            return self.val + 2

    DecoratorBase._init_ones_without_instance()
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_cb()() == 3


def test_class_method_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_init
        async def example(self):
            return self.val + 2

    DecoratorBase._init_ones_without_instance()
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(get_cb()()) == 3
