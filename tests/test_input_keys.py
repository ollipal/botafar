import pytest

import botafar

from .helpers import reset


def test_unknown_key():
    reset()
    with pytest.raises(RuntimeError):
        botafar.Button("?")


def test_known_key():
    reset()
    botafar.Button("A")
