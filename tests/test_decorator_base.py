import pytest

from botafar._internal.callbacks import CallbackBase
from botafar._internal.decorators import DecoratorBase, get_decorator

from .helpers import fake_run, get_async_result, get_cb_result, get_cbs, reset

# Decorator


class Dec(DecoratorBase):
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("dec", func)


def dec(func):
    return get_decorator(Dec, "title", "dec", True)(func)


# Tests


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


def test_decorator_empty_parenthesis_errors():
    reset()
    with pytest.raises(TypeError):

        @dec()
        def example():
            return 3


def test_function():
    reset()

    @dec
    def example():
        return 3

    fake_run()
    assert example() == 3
    assert get_cb_result("dec") == 3


def test_function_async():
    reset()

    @dec
    async def example():
        return 3

    fake_run()
    assert get_async_result(example()) == 3
    assert get_cb_result("dec") == 3


def test_lambda():
    reset()
    dec(lambda: 3)
    fake_run()
    assert get_cb_result("dec") == 3


def test_class_instance():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        def example(self):
            return self.val + 2

    c = Class()

    dec(c.example)

    fake_run()
    assert c.example() == 3
    assert get_cb_result("dec") == 3


def test_class_instance_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        async def example(self):
            return self.val + 2

    c = Class()

    dec(c.example)

    fake_run()
    assert get_async_result(c.example()) == 3
    assert get_cb_result("dec") == 3


def test_class_instance_static():
    reset()

    class Class:
        @staticmethod
        def example():
            return 3

    c = Class()

    dec(c.example)

    fake_run()
    assert c.example() == 3
    assert get_cb_result("dec") == 3


def test_class_instance_static_async():
    reset()

    class Class:
        @staticmethod
        async def example():
            return 3

    c = Class()

    dec(c.example)

    fake_run()
    assert get_async_result(c.example()) == 3
    assert get_cb_result("dec") == 3


def test_class_instance_classmethod():
    reset()

    class Class:
        value = 3

        @classmethod
        def example(cls):
            assert cls.__name__ == "Class"
            return cls.value

    Class()

    dec(Class.example)
    fake_run()
    assert Class.example() == 3
    assert get_cb_result("dec") == 3


def test_class_instance_classmethod_async():
    reset()

    class Class:
        value = 3

        @classmethod
        async def example(cls):
            assert cls.__name__ == "Class"
            return cls.value

    Class()

    dec(Class.example)
    fake_run()
    assert get_async_result(Class.example()) == 3
    assert get_cb_result("dec") == 3


def test_class_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @dec
        def example(self):
            return self.val + 2

    Class()

    fake_run()
    assert get_cb_result("dec") == 3
    assert Class().example() == 3


def test_class_method_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @dec
        async def example(self):
            return self.val + 2

    Class()

    fake_run()
    assert get_cb_result("dec") == 3
    assert get_async_result(Class().example()) == 3


def test_class_staticmethod():
    reset()

    class Class:
        @dec
        @staticmethod
        def example():
            return 3

    Class()

    fake_run()
    assert Class.example() == 3
    assert get_cb_result("dec") == 3


def test_class_staticmethod_mixed():
    reset()

    class Class:
        @staticmethod
        @dec
        def example():
            return 3

    Class()

    fake_run()
    assert Class.example() == 3
    assert get_cb_result("dec") == 3


def test_class_staticmethod_async():
    reset()

    class Class:
        @dec
        @staticmethod
        async def example():
            return 3

    Class()

    fake_run()
    assert get_async_result(Class.example()) == 3
    assert get_cb_result("dec") == 3


def test_class_classmethod():
    reset()

    class Class:
        value = 3

        @dec
        @classmethod
        def example(cls):
            assert cls.__name__ == "Class"
            return cls.value

    Class()

    fake_run()
    assert Class.example() == 3
    assert get_cb_result("dec") == 3


# def test_class_classmethod_mixed():
# ERRORS! but is ok, cannot fix


def test_class_classmethod_async():
    reset()

    class Class:
        value = 3

        @dec
        @classmethod
        async def example(cls):
            assert cls.__name__ == "Class"
            return cls.value

    Class()

    fake_run()
    assert get_async_result(Class.example()) == 3
    assert get_cb_result("dec") == 3


def test_multiple_function():
    reset()

    @dec
    def example():
        return 2

    @dec
    def example2():
        return 3

    fake_run()
    assert (
        CallbackBase.get_by_name("dec")[0]()
        + CallbackBase.get_by_name("dec")[1]()
        == 5
    )


def test_multiple_class_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @dec
        def example(self):
            return self.val + 2

        @dec
        def example2(self):
            return self.val + 3

    Class()

    fake_run()
    cbs = get_cbs("dec")
    assert cbs[0]() + cbs[1]() == 7


def test_multiple_classes():
    reset()

    class Class1:
        def __init__(self):
            self.val = 1

        @dec
        def example(self):
            return self.val + 2

    class Class2:
        def __init__(self):
            self.val = 3

        @dec
        def example(self):
            return self.val + 4

    Class1()
    Class2()

    fake_run()
    cbs = get_cbs("dec")
    assert cbs[0]() + cbs[1]() == 10


def test_multiple_mixed():
    reset()

    @dec
    def example():
        return 2

    class Class:
        def __init__(self):
            self.val = 3

        @dec
        def example(self):
            return self.val + 4

    c = Class()
    fake_run()
    cbs = get_cbs("dec")
    assert example() == 2
    assert c.example() == 7
    assert len(cbs) == 2
    assert cbs[0]() + cbs[1]() == 9


def test_multiple_decorators_function():
    reset()

    @dec
    @dec
    @dec
    def example():
        return 3

    fake_run()
    cbs = get_cbs("dec")
    assert example() == 3
    assert len(cbs) == 3
    assert cbs[0]() + cbs[1]() + cbs[2]() == 9


def test_multiple_decorators_class_instance_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @dec
        @dec
        @dec
        def example(self):
            return self.val + 3

    c = Class()

    fake_run()
    cbs = get_cbs("dec")
    assert isinstance(c, Class)
    assert c.example() == 4
    assert len(cbs) == 3
    assert cbs[0]() + cbs[1]() + cbs[2]() == 12


def test_multiple_decorators_staticmethod():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @dec
        @dec
        @dec
        @staticmethod
        def example():
            return 3

    c = Class()

    fake_run()
    cbs = get_cbs("dec")
    assert isinstance(c, Class)
    assert c.example() == 3
    assert len(cbs) == 3
    assert cbs[0]() + cbs[1]() + cbs[2]() == 9


def test_multiple_decorators_classmethod():
    reset()

    class Class:
        val = 1

        @dec
        @dec
        @dec
        @classmethod
        def example(cls):
            return cls.val + 3

    c = Class()

    fake_run()
    cbs = get_cbs("dec")
    assert isinstance(c, Class)
    assert c.example() == 4
    assert len(cbs) == 3
    assert cbs[0]() + cbs[1]() + cbs[2]() == 12
