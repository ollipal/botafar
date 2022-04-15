from ..callbacks import CallbackBase
from .decorator_base import DecoratorBase


class on_init(DecoratorBase):  # noqa: N801
    def verify_params_and_set_flags(self, params):
        pass

    def wrap(self, func):
        CallbackBase.register_callback("on_init", func)
        return func
