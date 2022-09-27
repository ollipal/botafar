import pytest

from botafar import on_init

from .helpers import fake_run, get_async_result, get_cb_result, reset


def test_on_init_empty_parenthesis_errors():
    reset()
    with pytest.raises(TypeError):

        @on_init()
        def example():
            return 3


def test_on_init_extra_kwargs_errors():
    reset()
    with pytest.raises(TypeError):

        @on_init(a=7)
        def example():
            return 3


def test_on_init_extra_args_errors():
    reset()
    with pytest.raises(TypeError):

        @on_init(7, 8)
        def example():
            return 3


def test_function():
    reset()

    @on_init
    def example():
        return 3

    fake_run()
    assert example() == 3
    assert get_cb_result("on_init") == 3


def test_function_async():
    reset()

    @on_init
    async def example():
        return 3

    fake_run()
    assert get_async_result(example()) == 3
    assert get_cb_result("on_init") == 3


def test_lambda():
    reset()
    on_init(lambda: 3)
    fake_run()
    assert get_cb_result("on_init") == 3


def test_class_instance():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        def example(self):
            return self.val + 2

    c = Class()

    on_init(c.example)

    fake_run()
    assert c.example() == 3
    assert get_cb_result("on_init") == 3


def test_class_instance_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        async def example(self):
            return self.val + 2

    c = Class()

    on_init(c.example)

    fake_run()
    assert get_async_result(c.example()) == 3
    assert get_cb_result("on_init") == 3


def test_class_instance_static():
    reset()

    class Class:
        @staticmethod
        def example():
            return 3

    c = Class()

    on_init(c.example)

    fake_run()
    assert c.example() == 3
    assert get_cb_result("on_init") == 3


def test_class_instance_static_async():
    reset()

    class Class:
        @staticmethod
        async def example():
            return 3

    c = Class()

    on_init(c.example)

    fake_run()
    assert get_async_result(c.example()) == 3
    assert get_cb_result("on_init") == 3


def test_class_classmethod():
    reset()

    class Class:
        val = 1

        @classmethod
        def example(cls):
            return cls.val + 3

    c = Class()

    on_init(c.example)

    fake_run()
    assert c.example() == 4
    assert get_cb_result("on_init") == 4


def test_class_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_init
        def example(self):
            return self.val + 2

    Class()

    fake_run()
    assert get_cb_result("on_init") == 3


def test_class_method_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_init
        async def example(self):
            return self.val + 2

    Class()

    fake_run()
    assert get_cb_result("on_init") == 3
