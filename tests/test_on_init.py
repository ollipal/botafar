import pytest

import telebotties as tb
from telebotties._internal.decorators import DecoratorBase


def test_exit_on_init():
    @tb.on_init
    def init():
        tb.exit()

    with pytest.raises(SystemExit):
        tb.listen()
