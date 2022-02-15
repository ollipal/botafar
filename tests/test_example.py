import pytest
import telebotties as tb

def test_unknown_key():
    with pytest.raises(AssertionError):
        tb.Button("?")

def test_known_key():
    tb.Button("A")
