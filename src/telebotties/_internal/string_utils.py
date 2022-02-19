def dim(string):
    return f"\033[2m{string}\033[0m"


def bold(string):
    return f"\033[1m{string}\033[0m"


def key(string):
    return f"\033[1;30;107m {string} \033[0m"
