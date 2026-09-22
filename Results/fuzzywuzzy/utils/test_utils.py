import sys
import os

# Ajuste del path para asegurar que la estructura de directorios permita importar 'utils'
# El archivo objetivo está en /Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/fuzzywuzzy/utils.py
sys.path.insert(0, '/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/fuzzywuzzy')

from utils import (
    validate_string, check_for_equivalence, check_for_none, 
    check_empty_string, asciidammit, make_type_consistent, 
    full_process, intr
)

def test_validate_string():
    assert validate_string("abc") is True
    assert validate_string("") is False
    assert validate_string(None) is False
    assert validate_string(123) is False

def test_decorators():
    @check_for_equivalence
    def dummy_eq(s1, s2): return 1
    
    @check_for_none
    def dummy_none(s1, s2): return 1
    
    @check_empty_string
    def dummy_empty(s1, s2): return 1

    assert dummy_eq("a", "a") == 100
    assert dummy_eq("a", "b") == 1

    assert dummy_none(None, "b") == 0
    assert dummy_none("a", "b") == 1

    assert dummy_empty("", "b") == 0
    assert dummy_empty("a", "b") == 1

def test_asciidammit():
    assert asciidammit("hello") == "hello"
    assert asciidammit("café") == "caf"
    assert asciidammit(123) == "123"

def test_make_type_consistent():
    # Verifica el retorno de tuplas consistentes
    s1, s2 = make_type_consistent("a", "b")
    assert s1 == "a"
    assert s2 == "b"
    
    # Verifica forzado a unicode/str
    s1, s2 = make_type_consistent("a", 1)
    assert s1 == "a"
    assert s2 == "1"

def test_full_process():
    # Verifica procesamiento básico
    result = full_process("  Hello World!  ")
    assert result == "hello world"
    
    # Verifica force_ascii
    result_ascii = full_process("café", force_ascii=True)
    assert result_ascii == "caf"

def test_intr():
    assert intr(2.4) == 2
    assert intr(2.6) == 3
    assert intr(2.5) == 2
    assert intr(3.5) == 4