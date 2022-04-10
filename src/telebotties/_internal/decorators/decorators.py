from ..callbacks import CallbackBase
from .decorator_base import DecoratorBase


class on_init(DecoratorBase):
    def __init__(self, *args, **kwargs):
        assert (
            kwargs == {}
        ), f"{self.__class__.__name__} takes no keyword parameters, now got: {kwargs}"
        assert (
            len(args) <= 1
        ), f"{self.__class__.__name__} got too many arguments: {args}"
        super().__init__(*args, **kwargs)

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func
