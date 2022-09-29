import os
import traceback


def dim(string):  # Also do italic, dim is not widely supported
    return f"\033[3;2m{string}\033[0m"


def bold(string):
    return f"\033[1m{string}\033[0m"


def cyan_bold(string):
    return f"\033[1;36m{string}\033[0m"


def underlined(string):
    return f"\033[4m{string}\033[0m"


def key(string):
    return f"\033[1;30;47m {string} \033[0m"


def blue_key(string):
    return f"\033[1;44;37m {string} \033[0m"


def error_to_string(e):
    return "".join(
        traceback.format_exception(type(e), e, e.__traceback__)
    ).rstrip()


def _get_padding_target(control_datas):
    """The actual target value makes no sense but it seems to work..."""
    target = 0
    for data in control_datas:
        keys_map = data["keys"]
        for key in data["has_callbacks"] + data["without_callbacks"]:
            keys = keys_map[key]
            length = 0
            for key in keys:
                length += len(key) + 5
            target = max(target, length)
    return target


def _color_keys(keys, color, target):
    ret = ""
    apparent_len = 0  # ASCII does not add to len
    for key_ in keys:
        apparent_len += len(key_) + 5
        ret += f"{blue_key(key_) if color == 'blue' else key(key_)} / "

    padding = " " * (target - apparent_len) if apparent_len < target else ""
    return ret[:-3] + padding


def control_list_string(control_datas):
    ret = ""
    target = _get_padding_target(control_datas)
    for data in control_datas:
        keys_map = data["keys"]
        for key in data["has_callbacks"]:
            description = data["titles"].get(key, ("Unknown action", 0))[0]
            ret += (
                f"{_color_keys(keys_map[key], 'blue', target)} "
                f"- {description}\n"
            )
        for key in data["without_callbacks"]:
            ret += (
                f"{_color_keys(keys_map[key], 'regular', target)} "
                "- No callbacks added\n"  # TODO add link to add cbs
            )

    # TODO add link to control documentation if no controls have been created
    return ret + "\n" if ret != "" else dim("(no controls created)\n")


def get_welcome_message(id):
    if os.environ.get("BOTAFAR_ENV") != "dev":
        return (
            "\nBot running, connect at "
            f"{cyan_bold(f'https://botafar.com/{id}')} "
            f"{dim('(ctrl + click to open)')}\n"
        )
    else:
        return (
            "\nBot running, connect at "
            f"{cyan_bold(f'http://localhost:5173/{id}')} "
            f"{dim('(ctrl + click to open)')}\n"
        )
