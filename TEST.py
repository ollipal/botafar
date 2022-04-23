class DecoratorBase:
    def __init__(self, *func):
        print(func[1:])
        self.func_original = func[0]

    # This is required for functions to stay callable
    def __call__(self, *args, **kwargs):
        return self.func_original(*args, **kwargs)

    # NOTE: this does not trigger for normal functions
    def __set_name__(self, owner, name):  # noqa: C901
        print("SETTING NAME")
        print(owner)
        print(name)


def trace(*args, **kwargs):
    print(args)

    def wrap(func):
        return DecoratorBase(*args)

    if len(args) == 1 and callable(args[0]):
        return wrap(args[0])
    elif len(args) == 0 and len(kwargs) == 0:
        raise RuntimeError("thing")
    else:
        return wrap


class Btn:
    def on_press(self, *args):
        return trace(*args)


b = Btn()


def on_time(func, time):
    return trace(func, time)


class Class:
    @b.on_press(1)
    def thing():
        pass

    """ @on_time(1)
    def thing2():
        pass """
