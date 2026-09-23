import pytest
from fuzz import (
    ratio, partial_ratio, token_sort_ratio, partial_token_sort_ratio,
    token_set_ratio, partial_token_set_ratio, QRatio, UQRatio, WRatio, UWRatio
)

def test_ratio():
    assert ratio("test", "test") == 100
    assert ratio("test", "tent") == 75
    assert ratio("", "a") == 0

def test_partial_ratio():
    assert partial_ratio("this is a test", "this is a test!") == 100
    assert partial_ratio("test", "this is a test") == 100
    assert partial_ratio("a", "b") == 0

def test_token_sort_ratio():
    assert token_sort_ratio("fuzzy wuzzy", "wuzzy fuzzy") == 100
    assert token_sort_ratio("a b c", "c b a") == 100
    assert token_sort_ratio("test", "") == 0

def test_partial_token_sort_ratio():
    assert partial_token_sort_ratio("fuzzy wuzzy", "wuzzy fuzzy") == 100
    assert partial_token_sort_ratio("a b c", "c b a d") == 100

def test_token_set_ratio():
    assert token_set_ratio("fuzzy wuzzy", "wuzzy fuzzy") == 100
    assert token_set_ratio("fuzzy wuzzy", "fuzzy wuzzy fuzzy") == 100
    assert token_set_ratio("a b c", "a b") == 100

def test_partial_token_set_ratio():
    assert partial_token_set_ratio("fuzzy wuzzy", "wuzzy fuzzy") == 100
    assert partial_token_set_ratio("a b c", "a b") == 100

def test_qratio():
    assert QRatio("test", "test") == 100
    assert QRatio("Test", "test") == 100
    assert QRatio("", "test") == 0
    assert QRatio(None, "test") == 0

def test_uqratio():
    assert UQRatio("test", "test") == 100
    assert UQRatio("test", "tést") < 100

def test_wratio():
    # Test identical strings
    assert WRatio("test", "test") == 100
    # Test significant length difference (triggers partial logic)
    assert WRatio("test", "this is a very long test string") > 0
    # Test empty strings
    assert WRatio("", "test") == 0
    assert WRatio(None, "test") == 0

def test_uwratio():
    assert UWRatio("test", "test") == 100
    assert UWRatio("tést", "tést") == 100

def test_edge_cases_none():
    # These functions are decorated with @utils.check_for_none
    # Depending on implementation, they return 0 or None when input is None
    assert ratio(None, "test") == 0
    assert partial_ratio(None, "test") == 0
    assert token_sort_ratio(None, "test") == 0
    assert token_set_ratio(None, "test") == 0

def test_edge_cases_empty():
    assert ratio("", "test") == 0
    assert partial_ratio("test", "") == 0
    assert token_sort_ratio("", "") == 0