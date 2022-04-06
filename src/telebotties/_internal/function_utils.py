from inspect import Parameter, signature

from varname import VarnameRetrievingError, nameof


def takes_parameter(function, param_name):
    parameters = signature(function).parameters.values()
    takes_param = False
    for i, param in enumerate(parameters):
        if i == 0:
            if param.name == param_name:
                takes_param = True
            elif param.kind == Parameter.POSITIONAL_ONLY:
                raise RuntimeError(
                    f"The first control callback argument must be called "
                    f"'{param_name}', or it needs to be optional. Currently "
                    f"it is '{param.name}' and it is required."
                )
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
                    "Callback arguments need to be optional, "
                    "except for the first one that can be required if it "
                    f"called '{param_name}'. Argument '{param.name}' should "
                    "be made optional or removed."
                )
    return takes_param


# NOTE: this should be used inside decorator, frame=3
def get_function_name(f):
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
        name = name.split(".")[-1]

    return name


if __name__ == "__main__":

    def decorator(f):
        name = get_function_name(f)
        print(name)
        return f

    @decorator
    def regular_function():
        pass

    class SampleClass:
        @decorator
        def regular_class_method(self):
            pass

        @decorator
        @staticmethod
        def static_class_method(self):
            pass

    # Using decorator indirectly:
    decorator(regular_function)
    named_lamda = lambda a: a + 10  # noqa:E731
    decorator(named_lamda)
    decorator(lambda a: a + 10)
    c = SampleClass()
    decorator(c.regular_class_method)
    decorator(SampleClass.static_class_method)
