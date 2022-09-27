import pytest

import botafar as tb

from .helpers import reset


def test_unknown_key():
    reset()
    with pytest.raises(RuntimeError):
        tb.Button("?")


def test_known_key():
    reset()
    tb.Button("A")
