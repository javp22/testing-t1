import sys
import os
import pytest

# Asegurar que el directorio del archivo fuzz.py está en el path para la importación relativa/absoluta
sys.path.insert(0, os.path.abspath(os.path.dirname('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/fuzzywuzzy/fuzz.py')))

from fuzz import (
    ratio, partial_ratio, token_sort_ratio, partial_token_sort_ratio,
    token_set_ratio, partial_token_set_ratio, QRatio, UQRatio, WRatio, UWRatio,
    _token_set
)

def test_ratio():
    assert ratio("test", "test") == 100
    assert ratio("test", "tent") == 75
    assert ratio("", "abc") == 0

def test_partial_ratio():
    assert partial_ratio("test", "this is a test string") == 100
    assert partial_ratio("abc", "123abc456") == 100
    assert partial_ratio("short", "longer string") < 100

def test_token_sort_ratio():
    assert token_sort_ratio("marcos antonio", "antonio marcos") == 100
    assert token_sort_ratio("test a b", "b a test") == 100

def test_partial_token_sort_ratio():
    assert partial_token_sort_ratio("marcos antonio", "roberto antonio marcos") == 100
    assert partial_token_sort_ratio("a b c", "c d e a b") == 100

def test_token_set_ratio():
    assert token_set_ratio("marcos antonio", "marcos antonio marcos") == 100
    assert token_set_ratio("a b c", "a b c d e") == 100
    assert token_set_ratio("test", "test") == 100

def test_partial_token_set_ratio():
    assert partial_token_set_ratio("marcos antonio", "marcos antonio extra words") == 100
    assert partial_token_set_ratio("a b", "a b c d e f") == 100

def test_qratio():
    assert QRatio("test", "test") == 100
    assert QRatio("  test  ", "test") == 100
    assert QRatio("", "test") == 0
    assert QRatio("test", "test", full_process=False) == 100

def test_uqratio():
    assert UQRatio("test", "test") == 100
    assert UQRatio("café", "café") == 100

def test_wratio():
    assert WRatio("test", "test") == 100
    assert WRatio("short", "this is a very long string that is much longer than the first") < 100
    assert WRatio("", "something") == 0
    assert WRatio("test", "test", full_process=False) == 100

def test_uwratio():
    assert UWRatio("café", "café") == 100
    assert UWRatio("test", "test") == 100

def test_token_set_internal_logic():
    # Prueba la rama donde full_process=False y s1 == s2
    assert _token_set("test", "test", full_process=False) == 100
    # Prueba la validación de string en _token_set
    assert _token_set("", "test", full_process=True) == 0