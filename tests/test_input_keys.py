import pytest

import telebotties as tb
from telebotties._internal.controls import ControlBase


def reset():
    ControlBase._event_callbacks = {}
    ControlBase._controls = []


def test_unknown_key():
    reset()
    with pytest.raises(RuntimeError):
        tb.Button("?")


def test_known_key():
    reset()
    tb.Button("A")
