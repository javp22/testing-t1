import pytest
import sys
import os

# Asegurar que el directorio del archivo original está en el PYTHONPATH
sys.path.insert(0, '/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/fuzzywuzzy')

from utils import (
    validate_string, check_for_equivalence, check_for_none, 
    check_empty_string, asciionly, asciidammit, 
    make_type_consistent, full_process, intr, unicode
)

def test_validate_string():
    assert validate_string("abc") is True
    assert validate_string("") is False
    assert validate_string(None) is False
    assert validate_string(123) is False
    assert validate_string([1]) is True

def test_check_for_equivalence():
    @check_for_equivalence
    def mock_func(a, b):
        return 0
    
    assert mock_func("a", "a") == 100
    assert mock_func("a", "b") == 0

def test_check_for_none():
    @check_for_none
    def mock_func(a, b):
        return 1
    
    assert mock_func(None, "b") == 0
    assert mock_func("a", None) == 0
    assert mock_func("a", "b") == 1

def test_check_empty_string():
    @check_empty_string
    def mock_func(a, b):
        return 1
    
    assert mock_func("", "b") == 0
    assert mock_func("a", "") == 0
    assert mock_func("a", "b") == 1

def test_asciionly():
    # 'é' es un caracter fuera del rango 0-127
    assert asciionly("abc") == "abc"
    assert "é" not in asciionly("café")

def test_asciidammit():
    assert asciidammit("abc") == "abc"
    # Probar con unicode y tipos no string
    assert asciidammit(unicode("café")) == "caf"
    assert asciidammit(123) == "123"

def test_make_type_consistent():
    s1, s2 = make_type_consistent("a", "b")
    assert isinstance(s1, str) and isinstance(s2, str)
    
    u1, u2 = make_type_consistent(1, 2)
    assert u1 == unicode("1") and u2 == unicode("2")

def test_full_process():
    # Verifica el flujo completo sin forzar ascii
    res = full_process("  Hello World 123!  ", force_ascii=False)
    assert res == "hello world 123"
    
    # Verifica el flujo forzando ascii
    res_ascii = full_process("café", force_ascii=True)
    assert "é" not in res_ascii

def test_intr():
    assert intr(2.4) == 2
    assert intr(2.6) == 3
    assert intr(3.5) == 4