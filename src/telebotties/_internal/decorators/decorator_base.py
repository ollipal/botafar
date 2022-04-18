import asyncio
import functools
import inspect
import types
from abc import ABC, abstractmethod
from inspect import Parameter, signature

from ..function_utils import get_function_title, get_params
from ..log_formatter import get_logger
from ..states import PRE_INIT, state_machine

logger = get_logger()
main = None


class DecoratorBase(ABC):
    _needs_wrapping = {}
    _wihtout_instance = set()
    _instance_callbacks = {}

    def __init__(self, *func):
        assert state_machine.state == PRE_INIT, (
            f"{self.__class__.__name__} callbacks cannot be added "
            "after listen()"
        )
        assert len(func) != 0, (
            "Remove empty parentheses '()' from "
            f"@tb.{self.__class__.__name__}()"
        )
        assert (
            len(func) == 1
        ), f"{self.__class__.__name__} got too many arguments: {func}"
        assert (
            not hasattr(func[0], "__name__") or func[0].__name__ != "__init__"
        ), f"Cannot add {self.__class__.__name__} callback to __init__ method"

        assert not inspect.isclass(
            func[0]
        ), f"Cannot use {self.__class__.__name__} with a class"
        assert isinstance(func[0], (classmethod, staticmethod)) or callable(
            func[0]
        ), (
            f"Cannot use {self.__class__.__name__} with a "
            f"non-callable object {func[0]}"
        )

        self.func = func[0]

        # flags to set in 'verify_params_and_set_flags'
        self.takes_event = False
        self.takes_time = False

        DecoratorBase._needs_wrapping[self.func] = (
            self.wrap,
            self.verify_params_and_set_flags,
        )

        self.func_title = get_function_title(self.func)
        # NOTE: this is not as good as functools.wraps:
        # https://stackoverflow.com/a/25973438/7388328
        # TODO: make sure this does something
        functools.update_wrapper(self, self.func)

    @abstractmethod
    def verify_params_and_set_flags(self, params):
        pass

    @abstractmethod
    def wrap(self, func):
        pass

    # This is required for functions to stay callable
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    # NOTE: this does not trigger for normal functions
    def __set_name__(self, owner, name):  # noqa: C901
        # Do the default __set_name__ action
        setattr(owner, name, self.func)

        # Make sure runs only once (not sure if even possible?)
        if not hasattr(owner, "__telebotties_instance_init_callbacks__") or (
            hasattr(owner, "__telebotties_instance_init_callbacks__")
            and self not in owner.__telebotties_instance_init_callbacks__
        ):

            def init_callback(self_):
                assert state_machine.state == PRE_INIT, (
                    f"{self.__class__.__name__} callbacks cannot be added "
                    "after listen()"
                )  # Should this be warning instead?
                assert not (self.takes_event and self.takes_time)

                if isinstance(self.func, (classmethod, staticmethod)):
                    if isinstance(self.func, classmethod):
                        params = list(get_params(self.func.__func__))[1:]
                    else:
                        params = get_params(self.func.__func__)

                    self.func = self.func.__func__
                    self.verify_params_and_set_flags(params)
                    params = []
                else:
                    params = get_params(self.func)
                    assert len(params) >= 1, "First param should be 'self'"
                    self.verify_params_and_set_flags(list(params)[1:])
                    params = [self_]

                if self.takes_time:
                    params.append(self.time)

                if asyncio.iscoroutinefunction(self.func):
                    if self.takes_event:

                        async def new_func(event):
                            return await getattr(owner, name)(*params, event)

                    else:

                        async def new_func():
                            return await getattr(owner, name)(*params)

                else:
                    if self.takes_event:

                        def new_func(event):
                            return getattr(owner, name)(*params, event)

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
        for func, (wrap, verify) in DecoratorBase._needs_wrapping.items():
            if isinstance(
                func, (types.FunctionType, types.LambdaType, types.MethodType)
            ):
                params = get_params(func)
                verify(params)
                wrap(func)
            elif hasattr(func, "__class__") and issubclass(
                func.__class__, DecoratorBase
            ):
                raise RuntimeError(
                    "Currently no support for multiple callbacks"
                )
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
