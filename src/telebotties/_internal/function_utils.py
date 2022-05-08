from inspect import Parameter, signature

from varname import VarnameRetrievingError, nameof


def get_params(function):
    return signature(function).parameters.values()


def takes_parameter(parameters, param_name, error_name=None):
    takes_param = False
    for i, param in enumerate(parameters):
        if i == 0:
            if param.name == param_name:
                takes_param = True
            elif (
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
                if error_name is None:
                    raise RuntimeError(
                        f"The first callback parameter must be called "
                        f"'{param_name}', or it needs to be optional. "
                        f"Currently it is '{param.name}' and it is "
                        "required."
                    )
                else:
                    raise RuntimeError(
                        f"{error_name} callback parameter must be called "
                        f"'{param_name}', or it needs to be optional. "
                        f"Currently it is '{param.name}' and it is "
                        "required."
                    )
            # else: is some optional param
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
                raise RuntimeError(
                    "Callback parameters need to be optional, "
                    "except for the first one that can be required if it is "
                    f"called '{param_name}'. Parameter '{param.name}' should "
                    "be made optional or removed."
                )
    return takes_param


def get_required_params(parameters):
    required = []
    for param in parameters:
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
            required.append(param.name)
    return required


# NOTE: this should be used inside decorator, frame=3
def get_function_title(f):
    name = None
    try:
        name = nameof(f, frame=3, vars_only=False)
    except VarnameRetrievingError:
        if hasattr(f, "__name__"):
            name = f.__name__
        elif hasattr(f, "__func__") and hasattr(f.__func__, "__qualname__"):
            name = f.__func__.__qualname__
        elif hasattr(f, "__qualname__"):
            name = f.__qualname__

    if name is not None:
        if name.startswith("lambda"):
            pass
        else:
            name = name.split(".")[-1]
            name = name.replace("_", " ").strip().capitalize()

    return name


if __name__ == "__main__":

    def decorator(f):
        name = get_function_title(f)
        print(name)
        return f

    @decorator
    def regular_function():
        pass

    class Class:
        @decorator
        def instance_method(self):
            pass

        @decorator
        @classmethod
        def class_method(cls):
            pass

        @decorator
        @staticmethod
        def static_method(self):
            pass

    # Using decorator indirectly:
    decorator(regular_function)
    named_lamda = lambda a: a + 10  # noqa:E731
    decorator(named_lamda)
    decorator(lambda a: a + 10)
    c = Class()
    decorator(c.instance_method)
    decorator(Class.class_method)
    decorator(Class.static_method)
