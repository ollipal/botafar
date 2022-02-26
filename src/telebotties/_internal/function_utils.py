from inspect import Parameter, signature


def takes_parameter(function, param_name):
    parameters = signature(function).parameters.values()
    takes_param = False
    for i, param in enumerate(parameters):
        if i == 0:
            if param.name == param_name:
                takes_param = True
            elif param.kind == Parameter.POSITIONAL_ONLY:
                raise RuntimeError(
                    f"The first input callback argument must be called "
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
