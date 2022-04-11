import asyncio
import functools
import inspect
import types
from abc import ABC, abstractmethod
from inspect import Parameter, signature

from ..log_formatter import get_logger
from ..states import state_machine

logger = get_logger()
main = None


class DecoratorBase(ABC):
    _needs_wrapping = {}
    _wihtout_instance = set()
    _instance_callbacks = {}

    def __init__(self, *args, **kwargs):
        assert state_machine.state == "pre_init", (
            f"{self.__class__.__name__} callbacks cannot be added "
            "after listen()"
        )
        assert len(args) != 0, (
            "Remove empty parentheses '()' from "
            f"@tb.{self.__class__.__name__}()"
        )
        assert (
            not hasattr(args[0], "__name__") or args[0].__name__ != "__init__"
        ), f"Cannot add {self.__class__.__name__} callback to __init__ method"

        assert not inspect.isclass(
            args[0]
        ), f"Cannot use {self.__class__.__name__} with a class"
        assert isinstance(args[0], (classmethod, staticmethod)) or callable(
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
        # Do the default __set_name__ action
        setattr(owner, name, self.func)

        # Make sure runs only once (not sure if even possible?)
        if not hasattr(owner, "__telebotties_instance_init_callbacks__") or (
            hasattr(owner, "__telebotties_instance_init_callbacks__")
            and self not in owner.__telebotties_instance_init_callbacks__
        ):

            def init_callback(self_):
                assert state_machine.state == "pre_init", (
                    f"{self.__class__.__name__} callbacks cannot be added "
                    "after listen()"
                ) # Should this be warning instead?

                if isinstance(self.func, (classmethod, staticmethod)):
                    params = []
                else:
                    params = [self_]

                if asyncio.iscoroutinefunction(self.func):

                    async def new_func():
                        return await getattr(owner, name)(*params)

                else:

                    def new_func():
                        return getattr(owner, name)(*params)

                self.wrap(new_func)

            # Save instance init callbacks
            if not hasattr(owner, "__telebotties_instance_init_callbacks__"):
                owner.__telebotties_instance_init_callbacks__ = {
                    self: init_callback
                }
            elif (
                hasattr(owner, "__telebotties_instance_init_callbacks__")
                and self not in owner.__telebotties_instance_init_callbacks__
            ):
                owner.__telebotties_instance_init_callbacks__[
                    self
                ] = init_callback

            if owner not in DecoratorBase._wihtout_instance:
                DecoratorBase._wihtout_instance.add(owner)

            cb_name = self.__class__.__name__
            if owner not in DecoratorBase._instance_callbacks:
                DecoratorBase._instance_callbacks[owner] = [cb_name]
            elif cb_name not in DecoratorBase._instance_callbacks[owner]:
                DecoratorBase._instance_callbacks[owner].append(cb_name)

            # Only functions need wrapping
            del DecoratorBase._needs_wrapping[self.func]

            def new_init(*args, **kwargs):
                logger.debug(f"Custom init running for {owner.__name__}")

                for (
                    callback
                ) in owner.__telebotties_instance_init_callbacks__.values():
                    callback(args[0])

                if owner in DecoratorBase._wihtout_instance:
                    DecoratorBase._wihtout_instance.remove(owner)
                owner.__telebotties_original_init__(*args, **kwargs)

            if not hasattr(owner, "__telebotties_original_init__"):
                setattr(owner, "__telebotties_original_init__", owner.__init__)
                setattr(owner, "__init__", new_init)
        else:
            logger.debug("Second __set_name__ ignored")

    @staticmethod
    def post_listen():
        DecoratorBase._warn_ones_without_instance()
        DecoratorBase._wrap_ones_without_wrapping()

    @staticmethod
    def _warn_ones_without_instance():
        join_str = "', '"
        for cls in list(DecoratorBase._wihtout_instance):
            if DecoratorBase.requires_only_self(
                cls.__telebotties_original_init__
            ):
                logger.warning(
                    f"No {cls.__name__} instances created. Callbacks '"
                    f"{join_str.join(DecoratorBase._instance_callbacks[cls])}"
                    "' will not trigger. Create a instance with '"
                    f"{cls.__name__}()' before 'listen()' to enable "
                    "callbacks."
                )
            else:
                logger.warning(
                    f"No {cls.__name__} instances created. Callbacks '"
                    f"{join_str.join(DecoratorBase._instance_callbacks[cls])}"
                    f"' will not trigger. Create a {cls.__name__} instance "
                    "before 'listen()' to enable callbacks."
                )

    @staticmethod
    def _wrap_ones_without_wrapping():
        for func, wrap in DecoratorBase._needs_wrapping.items():
            if isinstance(
                func, (types.FunctionType, types.LambdaType, types.MethodType)
            ):
                wrap(func)
            else:
                raise RuntimeError(
                    f"Cannot reate a callback for: {func}, type: {type(func)}"
                )

    @staticmethod
    def requires_only_self(function):
        parameters = signature(function).parameters.values()
        takes_self = False
        takes_others = False
        for i, param in enumerate(parameters):
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
