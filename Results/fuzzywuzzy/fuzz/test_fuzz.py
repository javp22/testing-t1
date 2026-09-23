import pytest
from fuzz import (
    ratio, partial_ratio, token_sort_ratio, partial_token_sort_ratio,
    token_set_ratio, partial_token_set_ratio, QRatio, UQRatio, WRatio, UWRatio
)

def test_ratio():
    assert ratio("test", "test") == 100
    assert ratio("test", "tent") == 75
    assert ratio("", "test") == 0

def test_partial_ratio():
    assert partial_ratio("test", "this is a test") == 100
    assert partial_ratio("abc", "123abc456") == 100
    assert partial_ratio("short", "loooooonger string") < 50

def test_token_sort_ratio():
    assert token_sort_ratio("fuzzy wuzzy", "wuzzy fuzzy") == 100
    assert token_sort_ratio("a b c", "c b a") == 100
    assert token_sort_ratio("test", "test") == 100

def test_partial_token_sort_ratio():
    assert partial_token_sort_ratio("fuzzy wuzzy", "wuzzy fuzzy test") == 100
    assert partial_token_sort_ratio("a b c", "c b a d") == 100

def test_token_set_ratio():
    assert token_set_ratio("fuzzy wuzzy", "wuzzy fuzzy fuzzy") == 100
    assert token_set_ratio("a b c", "a b") == 100
    assert token_set_ratio("data science", "science data") == 100

def test_partial_token_set_ratio():
    assert partial_token_set_ratio("a b c", "a b c d e f") == 100
    assert partial_token_set_ratio("test", "a test b") == 100

def test_qratio():
    assert QRatio("Test", "test") == 100
    assert QRatio("test", "") == 0
    assert QRatio("fuzzy", "wuzzy") == 0

def test_uqratio():
    assert UQRatio("Test", "test") == 100
    assert UQRatio("fuzzy", "wuzzy") == 0

def test_wratio():
    # Test identical
    assert WRatio("test", "test") == 100
    # Test significant length difference (triggers partial_scale logic)
    assert WRatio("a", "a" * 20) <= 100
    # Test short circuit
    assert WRatio("", "test") == 0
    assert WRatio(None, "test") == 0

def test_uwratio():
    assert UWRatio("test", "test") == 100
    assert UWRatio("a", "b") == 0

@pytest.mark.parametrize("func", [
    ratio, partial_ratio, token_sort_ratio, partial_token_sort_ratio,
    token_set_ratio, partial_token_set_ratio, QRatio, WRatio
])
def test_none_handling(func):
    # utils.check_for_none should catch these
    assert func(None, "test") == 0
    assert func("test", None) == 0
    assert func(None, None) == 0

def test_empty_string_handling():
    assert ratio("", "") == 0
    assert partial_ratio("", "test") == 0