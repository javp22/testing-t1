import sys
import types
from unittest.mock import MagicMock

# Configuracion del entorno para inyectar la dependencia faltante
mock_sp = MagicMock()
# Configuracion de los metodos estaticos esperados por el codigo original
mock_sp.replace_non_letters_non_numbers_with_whitespace = lambda s: s
mock_sp.to_lower_case = lambda s: s.lower()
mock_sp.strip = lambda s: s.strip()

string_processing = types.ModuleType("string_processing")
string_processing.StringProcessor = mock_sp
sys.modules["string_processing"] = string_processing

# Importacion directa del modulo desde la ruta correcta
sys.path.append("/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/fuzzywuzzy")
import utils

def test_validate_string():
    assert utils.validate_string("test") is True
    assert utils.validate_string("") is False
    assert utils.validate_string(None) is False
    assert utils.validate_string(123) is False

def test_check_for_equivalence():
    @utils.check_for_equivalence
    def mock_func(a, b):
        return 50
    assert mock_func("a", "a") == 100
    assert mock_func("a", "b") == 50

def test_check_for_none():
    @utils.check_for_none
    def mock_func(a, b):
        return 50
    assert mock_func(None, "b") == 0
    assert mock_func("a", None) == 0
    assert mock_func("a", "b") == 50

def test_check_empty_string():
    @utils.check_empty_string
    def mock_func(a, b):
        return 50
    assert mock_func("", "b") == 0
    assert mock_func("a", "") == 0
    assert mock_func("a", "b") == 50

def test_asciidammit():
    assert utils.asciidammit("abc") == "abc"
    assert utils.asciidammit("abc\u00A0") == "abc"
    assert utils.asciidammit(123) == "123"

def test_make_type_consistent():
    r1, r2 = utils.make_type_consistent("a", "b")
    assert isinstance(r1, str)
    assert isinstance(r2, str)
    r3, r4 = utils.make_type_consistent("a", 1)
    assert isinstance(r3, str)
    assert r4 == "1"

def test_full_process():
    assert utils.full_process("  AbC 123!!  ") == "abc 123"
    assert utils.full_process("AbC\u00A0 123", force_ascii=True) == "abc 123"

def test_intr():
    assert utils.intr(1.4) == 1
    assert utils.intr(1.6) == 2
    assert utils.intr(0) == 0
    assert utils.intr(2.5) == 2