import asyncio

import pytest

from telebotties import Button
from telebotties._internal.callbacks import CallbackBase
from telebotties._internal.controls import ControlBase
from telebotties._internal.decorators import DecoratorBase
from telebotties._internal.events import Event

# HELPERS


def get_cbs(name):
    return ControlBase._get_callbacks(Event(name, "player", "A"))


def get_cb(name):
    callbacks = get_cbs(name)
    assert len(callbacks) == 1
    return callbacks[0]


def reset():
    CallbackBase._callbacks = {}
    DecoratorBase._needs_wrapping = {}
    DecoratorBase._wihtout_instance = set()
    ControlBase._event_callbacks = {}
    ControlBase._controls = []


def get_async_result(func):
    return asyncio.run(func)


# TESTS


def test_non_callable_errors():
    reset()
    with pytest.raises(AssertionError):
        b = Button("A")
        b.on_press("potato")


def test_class_decorator_errors():
    reset()
    with pytest.raises(AssertionError):
        b = Button("A")

        @b.on_press
        class Class:
            pass


def test_on_init_empty_parenthesis_errors():
    reset()
    with pytest.raises(AssertionError):

        b = Button("A")

        @b.on_press()
        def example():
            return 3

    reset()
    with pytest.raises(AssertionError):

        b = Button("A")

        @b.on_release()  # noqa: F811
        def example():
            return 3

    reset()
    with pytest.raises(AssertionError):

        b = Button("A")

        @b.on_any()  # noqa: F811
        def example():
            return 3


def test_function_wrong_param_errors():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        @b.on_press
        def example(other):
            return 3

        DecoratorBase.post_listen()


def test_function_any_no_event_errors():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        @b.on_any
        def example():
            return 3

        DecoratorBase.post_listen()


def test_function_wrong_param_errors_2():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        @b.on_press
        def example(event, other):
            return 3

        DecoratorBase.post_listen()


def test_class_method_wrong_param_errors():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        class Class:
            def __init__(self):
                self.val = 1

            @b.on_press
            def example(self, other):
                return self.val + 2

        Class()


def test_class_method_wrong_param_errors_2():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        class Class:
            def __init__(self):
                self.val = 1

            @b.on_press
            def example(self, event, other):
                return self.val + 2

        Class()


def test_class_method_any_no_event_errors():
    reset()
    b = Button("A")

    with pytest.raises(RuntimeError):

        class Class:
            def __init__(self):
                self.val = 1

            @b.on_any
            def example(self):
                return self.val + 2

        Class()


def test_function():
    reset()
    b = Button("A")

    @b.on_press
    def example():
        return 3

    DecoratorBase.post_listen()
    assert example() == 3
    assert get_cb("on_press")() == 3


def test_function_event():
    reset()
    b = Button("A")

    @b.on_press
    def example(event):
        return event

    DecoratorBase.post_listen()
    assert example(1) == 1
    assert get_cb("on_press")(1) == 1


def test_function_async():
    reset()
    b = Button("A")

    @b.on_press
    async def example():
        return 3

    DecoratorBase.post_listen()
    assert get_async_result(example()) == 3
    assert get_async_result(get_cb("on_press")()) == 3


def test_lambda():
    reset()
    Button("A").on_press(lambda: 3)
    DecoratorBase.post_listen()
    assert get_cb("on_press")() == 3


def test_class_instance():
    reset()
    b = Button("A")

    class Class:
        def __init__(self):
            self.val = 1

        def example(self):
            return self.val + 2

    c = Class()

    b.on_press(c.example)

    DecoratorBase.post_listen()
    assert c.example() == 3
    assert get_cb("on_press")() == 3


def test_class_instance_static():
    reset()
    b = Button("A")

    class Class:
        @staticmethod
        def example():
            return 3

    c = Class()

    b.on_press(c.example)

    DecoratorBase.post_listen()
    assert c.example() == 3
    assert get_cb("on_press")() == 3


def test_class_instance_static_event():
    reset()
    b = Button("A")

    class Class:
        @staticmethod
        def example(event):
            return event

    c = Class()

    b.on_press(c.example)

    DecoratorBase.post_listen()
    assert c.example(3) == 3
    assert get_cb("on_press")(3) == 3


def test_class_instance_classmethod():
    reset()
    b = Button("A")

    class Class:
        value = 3

        @classmethod
        def example(cls):
            assert cls.__name__ == "Class"
            return cls.value

    Class()

    b.on_press(Class.example)
    DecoratorBase.post_listen()
    assert Class.example() == 3
    assert get_cb("on_press")() == 3


def test_class_instance_classmethod_event():
    reset()
    b = Button("A")

    class Class:
        value = 3

        @classmethod
        def example(cls, event):
            assert cls.__name__ == "Class"
            return event

    Class()

    b.on_press(Class.example)
    DecoratorBase.post_listen()
    assert Class.example(3) == 3
    assert get_cb("on_press")(3) == 3


def test_class_method():
    reset()
    b = Button("A")

    class Class:
        def __init__(self):
            self.val = 1

        @b.on_press
        def example(self):
            return self.val + 2

    Class()

    DecoratorBase.post_listen()
    assert get_cb("on_press")() == 3
    assert Class().example() == 3


def test_class_method_event():
    reset()
    b = Button("A")

    class Class:
        def __init__(self):
            self.val = 1

        @b.on_press
        def example(self, event):
            return event

    Class()

    DecoratorBase.post_listen()
    assert get_cb("on_press")(3) == 3
    assert Class().example(3) == 3


def test_multiple_class_method():
    reset()
    b = Button("A")

    class Class:
        def __init__(self):
            self.val = 1

        @b.on_press
        def example(self):
            return self.val + 2

        @b.on_press
        def example2(self):
            return self.val + 3

    Class()

    DecoratorBase.post_listen()
    callbacks = get_cbs("on_press")
    assert callbacks[0]() + callbacks[1]() == 7


def test_multiple_classes():
    reset()
    b = Button("A")

    class Class1:
        def __init__(self):
            self.val = 1

        @b.on_press
        def example(self):
            return self.val + 2

    class Class2:
        def __init__(self):
            self.val = 3

        @b.on_press
        def example(self):
            return self.val + 4

    Class1()
    Class2()

    DecoratorBase.post_listen()
    callbacks = get_cbs("on_press")
    assert callbacks[0]() + callbacks[1]() == 10


def test_function_any():
    reset()
    b = Button("A")

    @b.on_any
    def example(event):
        return event

    DecoratorBase.post_listen()
    assert example(3) == 3
    assert get_cb("on_press")(3) == 3


def test_class_method_any():
    reset()
    b = Button("A")

    class Class:
        def __init__(self):
            self.val = 1

        @b.on_any
        def example(self, event):
            return event

    Class()

    DecoratorBase.post_listen()
    assert get_cb("on_press")(3) == 3
    assert Class().example(3) == 3
