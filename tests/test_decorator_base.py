import asyncio

import pytest

from telebotties._internal.callbacks import CallbackBase
from telebotties._internal.decorators import DecoratorBase

# HELPERS


class dec(DecoratorBase):
    def wrap(self, func):
        CallbackBase.register_callback("dec", func)


def get_cb():
    assert len(CallbackBase.get_by_name("dec")) == 1
    return CallbackBase.get_by_name("dec")[0]


def reset():
    CallbackBase._callbacks = {}
    DecoratorBase._needs_wrapping = {}
    DecoratorBase._wihtout_instance = set()


def get_async_result(func):
    return asyncio.run(func)


# TESTS


def test_non_callable_errors():
    reset()
    with pytest.raises(AssertionError):
        dec("potato")


def test_class_decorator_errors():
    reset()
    with pytest.raises(AssertionError):

        @dec
        class Class:
            pass


def test_classmethod_decorator_errors():
    reset()
    with pytest.raises(AssertionError):

        class Class:
            @dec
            @classmethod
            def example(cls):
                pass


def test_decorator_empty_parenthesis_errors():
    reset()
    with pytest.raises(AssertionError):

        @dec()
        def example():
            return 3


def test_classmethod_instance():
    reset()

    class Class:
        @classmethod
        def example(cls):
            return 3

    # TODO THIS SHOULD PROBABLY ERROR? TEST WITH MORE PARAMS
    dec(Class.example)
    DecoratorBase._wrap_ones_without_wrapping()
    assert Class.example() == 3
    assert get_cb()() == 3


def test_function():
    reset()

    @dec
    def example():
        return 3

    DecoratorBase._wrap_ones_without_wrapping()
    assert example() == 3
    assert get_cb()() == 3


def test_function_async():
    reset()

    @dec
    async def example():
        return 3

    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(example()) == 3
    assert get_async_result(get_cb()()) == 3


def test_lambda():
    reset()
    dec(lambda: 3)
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_cb()() == 3


def test_class_instance():
    reset()

    class Class:
        def example(self):
            return 3

    c = Class()

    dec(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert c.example() == 3
    assert get_cb()() == 3


def test_class_instance_async():
    reset()

    class Class:
        async def example(self):
            return 3

    c = Class()

    dec(c.example)

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

    dec(c.example)

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

    dec(c.example)

    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(c.example()) == 3
    assert get_async_result(get_cb()()) == 3


def test_class_method():
    reset()

    class Class:
        @dec
        def example(self):
            return 3

    DecoratorBase._init_ones_without_instance()
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_cb()() == 3


def test_class_method_async():
    reset()

    class Class:
        @dec
        async def example(self):
            return 3

    DecoratorBase._init_ones_without_instance()
    DecoratorBase._wrap_ones_without_wrapping()
    assert get_async_result(get_cb()()) == 3


"""
- without braces
- with braces
- with keyvalues

- with passable event

- test requires only self

etc.
"""
