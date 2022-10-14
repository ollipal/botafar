import asyncio
import functools
import inspect
import types
from abc import ABC, abstractmethod
from collections import OrderedDict
from inspect import Parameter, signature

from ..function_utils import get_function_title, get_params
from ..log_formatter import get_logger
from ..states import PRE_INIT, state_machine

logger = get_logger()
main = None


def get_decorator(cls, title, name, always_empty):
    def decorator(*args, **kwargs):
        assert not (always_empty and len(args) == 0 and len(kwargs) == 0), (
            "Remove empty parentheses '()' from " f"@botafar.{name}()"
        )
        assert not (
            always_empty and len(kwargs) != 0
        ), f"@botafar.{name} got unknown parameters {list(kwargs.keys())}"
        assert not (
            always_empty and len(args) > 1
        ), f"@botafar.{name} got unknown arguments {args}"
        assert not (
            always_empty
            and not (
                isinstance(args[0], (classmethod, staticmethod))
                or callable(args[0])
            )
        ), (f"Cannot use {name} with a " f"non-callable object {args[0]}")

        def wrap(title, *args, **kwargs):
            return cls(title, name, *args, **kwargs)

        if len(args) >= 1 and (
            isinstance(args[0], (classmethod, staticmethod))
            or callable(args[0])
        ):
            return wrap(title, *args, **kwargs)
        else:

            def wrap2(func):
                title = get_function_title(func)
                return wrap(title, func, *args, **kwargs)  # Saves kwargs

            return wrap2

    return decorator


class DecoratorBase(ABC):
    _needs_wrapping = OrderedDict()
    _wihtout_instance = set()
    _instance_callbacks = OrderedDict()

    def __init__(self, title, decorator_name, *args, **kwargs):
        self.decorator_name = decorator_name
        assert state_machine.state == PRE_INIT, (
            f"{self.decorator_name} callbacks cannot be added "
            "after botafar.run()"
        )
        assert (
            len(args) == 1
        ), f"{self.decorator_name} got too many arguments: {args}"
        assert (
            not hasattr(args[0], "__name__") or args[0].__name__ != "__init__"
        ), f"Cannot add {self.decorator_name} callback to __init__ method"

        assert not inspect.isclass(
            args[0]
        ), f"Cannot use {self.decorator_name} with a class"
        assert isinstance(args[0], (classmethod, staticmethod)) or callable(
            args[0]
        ), (
            f"Cannot use {self.decorator_name} with a "
            f"non-callable object {args[0]}"
        )

        self.func_original = args[0]
        self.func = args[0]

        # flags to set in 'verify_params_and_set_flags'
        self.takes_event = False
        self.takes_time = False

        self.init_finished = False

        DecoratorBase._needs_wrapping[self.func_original] = self

        self.func_title = title
        # NOTE: this is not as good as functools.wraps:
        # https://stackoverflow.com/a/25973438/7388328
        # TODO: make sure this does something
        functools.update_wrapper(self, self.func_original)

    @abstractmethod
    def verify_params_and_set_flags(self, params):
        pass

    @abstractmethod
    def wrap(self, func):
        pass

    # This is required for functions to stay callable
    def __call__(self, *args, **kwargs):
        return self.func_original(*args, **kwargs)

    # NOTE: this does not trigger for normal functions
    def __set_name__(self, owner, name):  # noqa: C901
        # Do the default __set_name__ action
        setattr(owner, name, self.func)

        # Do custom things
        def init_callback(self_):
            assert state_machine.state == PRE_INIT, (
                f"{self.decorator_name} callbacks cannot be added "
                "after listen()"
            )  # Should this be warning instead?
            assert not (self.takes_event and self.takes_time)

            if isinstance(self.func, (classmethod, staticmethod)):
                if isinstance(self.func, classmethod):
                    params = list(get_params(self.func.__func__))[1:]
                else:
                    params = get_params(self.func.__func__)

                self.verify_params_and_set_flags(params)
                params = []
            else:
                params = get_params(self.func)
                assert len(params) >= 1, "First param should be 'self'"
                self.verify_params_and_set_flags(list(params)[1:])
                params = [self_]

            self.init_callback_wrap(
                self.func,
                owner,
                name,
                params,
                self.takes_event,
                self.takes_time,
            )
            self.init_finished = True
            self.owner = owner
            self.name = name
            self.params = params

        # Save instance init callbacks
        if not hasattr(owner, "__botafar_instance_init_callbacks__"):
            owner.__botafar_instance_init_callbacks__ = {self: init_callback}
        elif (
            hasattr(owner, "__botafar_instance_init_callbacks__")
            and self not in owner.__botafar_instance_init_callbacks__
        ):
            owner.__botafar_instance_init_callbacks__[self] = init_callback

        if owner not in DecoratorBase._wihtout_instance:
            DecoratorBase._wihtout_instance.add(owner)

        cb_name = self.decorator_name
        if owner not in DecoratorBase._instance_callbacks:
            DecoratorBase._instance_callbacks[owner] = [cb_name]
        elif cb_name not in DecoratorBase._instance_callbacks[owner]:
            DecoratorBase._instance_callbacks[owner].append(cb_name)

        # Only functions need wrapping
        # if self.func_original in DecoratorBase._needs_wrapping:
        del DecoratorBase._needs_wrapping[self.func_original]

        def new_init(*args, **kwargs):
            logger.debug(f"Custom init running for {owner.__name__}")

            for callback in owner.__botafar_instance_init_callbacks__.values():
                callback(args[0])

            if owner in DecoratorBase._wihtout_instance:
                DecoratorBase._wihtout_instance.remove(owner)
            owner.__botafar_original_init__(*args, **kwargs)

        if not hasattr(owner, "__botafar_original_init__"):
            setattr(owner, "__botafar_original_init__", owner.__init__)
            setattr(owner, "__init__", new_init)

        # DecoratorBase._wrap_ones_without_wrapping()

    def init_callback_wrap(
        self, func, owner, name, params, takes_event, takes_time
    ):

        if isinstance(func, (classmethod, staticmethod)):
            func = func.__func__

        if asyncio.iscoroutinefunction(func):
            if takes_event:

                async def new_func(event):
                    return await getattr(owner, name)(*params, event)

            elif takes_time:

                async def new_func(time):
                    return await getattr(owner, name)(*params, time)

            else:

                async def new_func():
                    return await getattr(owner, name)(*params)

        else:
            if takes_event:

                def new_func(event):
                    return getattr(owner, name)(*params, event)

            elif takes_time:

                def new_func(time):
                    return getattr(owner, name)(*params, time)

            else:

                def new_func():
                    return getattr(owner, name)(*params)

        self.wrap(new_func)

    @staticmethod
    def post_listen():
        DecoratorBase._warn_ones_without_instance()
        DecoratorBase._wrap_ones_without_wrapping()

    @staticmethod
    def _warn_ones_without_instance():
        join_str = "', '"
        for cls in list(DecoratorBase._wihtout_instance):
            if (
                hasattr(cls, "botafar_ignore_no_instance")
                and cls.botafar_ignore_no_instance is True
            ):
                continue  # TODO document this?

            if DecoratorBase.requires_only_self(cls.__botafar_original_init__):
                logger.warning(
                    f"No {cls.__name__} instances created. Callbacks '"
                    f"{join_str.join(DecoratorBase._instance_callbacks[cls])}"
                    "' will not trigger. Create an instance with '"
                    f"{cls.__name__}()' before 'botafar.run()' to enable "
                    "callbacks."
                )
            else:
                logger.warning(
                    f"No {cls.__name__} instances created. Callbacks '"
                    f"{join_str.join(DecoratorBase._instance_callbacks[cls])}"
                    f"' will not trigger. Create at least one {cls.__name__} "
                    "instance before 'botafar.run()' to enable callbacks."
                )

    @staticmethod
    def _wrap_ones_without_wrapping():
        # Pass owner and params 'up' as long as possible
        # This makes stacked decorators work
        while True:
            del_list = []
            for func, self_ in DecoratorBase._needs_wrapping.items():
                if self_.init_finished is True:
                    func.init_callback_wrap(
                        func,
                        self_.owner,
                        self_.name,
                        self_.params,
                        self_.takes_event,
                        self_.takes_time,
                    )
                    func.init_finished = True
                    func.owner = self_.owner
                    func.name = self_.name
                    func.params = self_.params
                    func.takes_event = self_.takes_event
                    func.takes_time = self_.takes_time
                    func.func_title = self_.func_title
                    del_list.append(func)

            if len(del_list) == 0:
                break

            for func in del_list:
                del DecoratorBase._needs_wrapping[func]

        for func, self_ in DecoratorBase._needs_wrapping.items():
            if isinstance(
                func,
                (
                    types.FunctionType,
                    types.LambdaType,
                    types.MethodType,
                    DecoratorBase,
                ),
            ):
                params = get_params(func)
                self_.verify_params_and_set_flags(params)
                self_.wrap(func)
                self_.has_wrapped = True
            else:
                raise RuntimeError(
                    f"Cannot reate a callback for: {func}, type: {type(func)}"
                )

        # DecoratorBase._needs_wrapping = OrderedDict()

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
