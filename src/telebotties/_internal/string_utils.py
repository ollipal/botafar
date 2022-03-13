import traceback


def dim(string):
    return f"\033[2m{string}\033[0m"


def bold(string):
    return f"\033[1m{string}\033[0m"


def underlined(string):
    return f"\033[4m{string}\033[0m"


def key(string):
    return f"\033[1;7m {string} \033[0m"


def blue_key(string):
    return f"\033[1;44;37m {string} \033[0m"


def function_name_to_sentence(string):
    return string.replace("_", " ").strip().capitalize()


def error_to_string(e):
    return "".join(traceback.format_exception(type(e), e, e.__traceback__))


def _color_keys(keys, color):
    ret = ""
    apparent_len = 0  # ASCII does not add to len
    for key_ in keys:
        apparent_len += len(key_) + 5
        ret += f"{blue_key(key_) if color == 'blue' else key(key_)} / "

    target = 16
    padding = " " * (target - apparent_len) if apparent_len < target else ""
    return ret[:-3] + padding


def input_list_string(input_datas):
    ret = ""
    for data in input_datas:
        keys_map = data["keys"]
        for key in data["has_callbacks"]:
            description = data["titles"].get(key, "Unknown action")
            description = function_name_to_sentence(description)
            ret += f"{_color_keys(keys_map[key], 'blue')} - {description}\n"
        for key in data["without_callbacks"]:
            ret += (
                f"{_color_keys(keys_map[key], 'regular')} "
                "- No callbacks registered\n"
            )

    return ret + "\n" if ret != "" else dim("(no custom inputs registered)")
