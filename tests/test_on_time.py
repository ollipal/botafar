from telebotties import on_time_0

from .helpers import fake_listen, get_async_result, get_cb_result, reset


def test_function():
    reset()

    @on_time_0
    def example():
        return 3

    fake_listen()
    assert example() == 3
    assert get_cb_result("on_time") == 3


def test_function_async():
    reset()

    @on_time_0
    async def example():
        return 3

    fake_listen()
    assert get_async_result(example()) == 3
    assert get_cb_result("on_time") == 3


def test_class_method():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_time_0
        def example(self):
            return self.val + 2

    Class()

    fake_listen()
    assert get_cb_result("on_time") == 3


def test_class_method_async():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_time_0
        async def example(self):
            return self.val + 2

    Class()

    fake_listen()
    assert get_cb_result("on_time") == 3


def test_class_staticmethod():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_time_0
        @staticmethod
        def example():
            return 2

    Class()

    fake_listen()
    assert get_cb_result("on_time") == 2


def test_class_classmethod():
    reset()

    class Class:
        val = 1

        @on_time_0
        @classmethod
        def example(cls):
            return cls.val + 2

    Class()

    fake_listen()
    assert get_cb_result("on_time") == 3


def test_class_method_time():
    reset()

    class Class:
        def __init__(self):
            self.val = 1

        @on_time_0
        def example(self, time):
            val2 = 7 if time == 0 else 1
            return self.val + 2 + val2

    Class()

    fake_listen()
    assert get_cb_result("on_time") == 10
