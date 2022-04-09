import asyncio
import functools
import inspect
import types
from abc import ABC, abstractmethod
from inspect import Parameter, signature


class DecoratorBase(ABC):
    _needs_wrapping = {}
    _wihtout_instance = set()
    _funcs = []

    def __init__(self, *args, **kwargs):
        assert (
            len(args) != 0
        ), f"Remove empty parentheses '()' from @{self.__class__.__name__}()"
        assert not inspect.isclass(
            args[0]
        ), f"Cannot use {self.__class__.__name__} with a class"
        assert not isinstance(
            args[0], classmethod
        ), f"Cannot use {self.__class__.__name__} with a classmethod"
        assert callable(
            args[0]
        ), (
            f"Cannot use {self.__class__.__name__} with a "
            f"non-callable object {args[0]}"
        )

        self.func = args[0]
        self.args = args[1:]
        self.kwargs = kwargs
        DecoratorBase._needs_wrapping[self.func] = self.wrap

        # NOTE: this is not as good as functools.wraps:
        # https://stackoverflow.com/a/25973438/7388328
        functools.update_wrapper(self, self.func)

    # @abstractmethod
    # def check_signature(self, func):
    #    pass

    @abstractmethod
    def wrap(self, func):
        pass

    # This is required for functions to stay callable
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    # NOTE: this does not trigger for normal functions
    def __set_name__(self, owner, name):
        assert name != "__init__", "Cannot add callback to __init__ method"

        # Do the default __set_name__ action
        setattr(owner, name, self.func)

        if not hasattr(owner, "__original_init__"):
            DecoratorBase._wihtout_instance.add(owner)
            del DecoratorBase._needs_wrapping[self.func]

            def new_init(*args, **kwargs):
                print("Custom init running")
                if isinstance(self.func, staticmethod):
                    self.func = self.func.__func__
                else:
                    # def new():
                    # return self.func(args[0])
                    #    return self.func(args[0])
                    # self.func = lambda: getattr(owner, name)(args[0])
                    if asyncio.iscoroutinefunction(self.func):

                        async def new_func():
                            return await getattr(owner, name)(owner)

                    else:

                        def new_func():
                            return getattr(owner, name)(owner)

                    # self.func = new
                    self.func = new_func

                self.wrap(self.func)

                DecoratorBase._wihtout_instance.remove(owner)
                owner.__original_init__(*args, **kwargs)

            setattr(owner, "__original_init__", owner.__init__)
            setattr(owner, "__init__", new_init)

    @staticmethod
    def _init_ones_without_instance():
        for cls in list(DecoratorBase._wihtout_instance):
            cls()

    @staticmethod
    def _wrap_ones_without_wrapping():
        for func, wrap in DecoratorBase._needs_wrapping.items():
            print(f"HERE {inspect.ismethod(func)}")
            if isinstance(
                func, (types.FunctionType, types.LambdaType)
            ):  # __set_name__ won't be called
                print("IS FUNCTION")
                wrap(func)
            elif isinstance(
                func, types.MethodType
            ):  # __set_name__ won't be called
                print("IS METHOD")
                wrap(func)


def requires_only_self(function):
    parameters = signature(function).parameters.values()
    takes_self = False
    takes_others = False
    for i, param in enumerate(parameters):
        print(param.name)
        if i == 0:
            if param.name == "self":
                takes_self = True
            elif param.kind == Parameter.POSITIONAL_ONLY:
                takes_self = False
        else:
            if (
                (
                    param.kind == Parameter.POSITIONAL_OR_KEYWORD
                    and param.default == Parameter.empty
                )
                or param.kind  # Reguired positional or keyword argument
                == Parameter.POSITIONAL_ONLY
                or (  # Reguired positional argument
                    param.kind == Parameter.KEYWORD_ONLY
                    and param.default == Parameter.empty
                )  # Required keyword only argument
            ):
                takes_others = True
    return takes_self and not takes_others


if __name__ == "__main__":

    class Class:
        def __init__(self):
            print("Class")

        @DecoratorBase
        def test(self):
            print("test!!!")

    # b = Class()
    # b.test()

    @DecoratorBase
    def test2():
        print("test2")

    DecoratorBase._init_ones_without_instance()

    class Test:
        def __init__(self, name="Bob"):
            super().__init__()

    print(requires_only_self(test.__init__))
