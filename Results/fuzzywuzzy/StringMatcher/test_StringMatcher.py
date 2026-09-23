import pytest
import sys
from unittest.mock import MagicMock
from warnings import catch_warnings

# Mockear el módulo externo 'Levenshtein' antes de importar el archivo objetivo,
# ya que no está disponible en el entorno de ejecución.
sys.modules['Levenshtein'] = MagicMock()

# Importar las funciones mockeadas para simular el comportamiento esperado
import Levenshtein
Levenshtein.opcodes = MagicMock(return_value=[('equal', 0, 1, 0, 1)])
Levenshtein.editops = MagicMock(return_value=[('replace', 0, 0)])
Levenshtein.matching_blocks = MagicMock(return_value=[(0, 0, 1), (1, 1, 0)])
Levenshtein.ratio = MagicMock(return_value=1.0)
Levenshtein.distance = MagicMock(return_value=3)

# Ajustar el path para asegurar la importación del módulo objetivo
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/fuzzywuzzy')

from StringMatcher import StringMatcher

def test_initialization():
    matcher = StringMatcher(seq1="apple", seq2="pear")
    assert matcher._str1 == "apple"
    assert matcher._str2 == "pear"

def test_isjunk_warning():
    with catch_warnings(record=True) as w:
        StringMatcher(isjunk=lambda x: True)
        assert len(w) == 1
        assert "isjunk not NOT implemented" in str(w[-1].message)

def test_set_methods_and_reset():
    matcher = StringMatcher()
    matcher.set_seq1("test")
    matcher.set_seq2("text")
    assert matcher._str1 == "test"
    assert matcher._str2 == "text"
    
    matcher.ratio()
    assert matcher._ratio is not None
    
    matcher.set_seqs("a", "b")
    assert matcher._ratio is None
    assert matcher._str1 == "a"

def test_distance():
    matcher = StringMatcher(seq1="kitten", seq2="sitting")
    assert matcher.distance() == 3
    assert matcher._distance == 3

def test_ratio_and_quick_ratio():
    matcher = StringMatcher(seq1="hello", seq2="hello")
    assert matcher.ratio() == 1.0
    assert matcher.quick_ratio() == 1.0

def test_real_quick_ratio():
    matcher = StringMatcher(seq1="abc", seq2="abcdef")
    assert matcher.real_quick_ratio() == pytest.approx(0.6666666666666666)

def test_get_opcodes():
    matcher = StringMatcher(seq1="cat", seq2="cut")
    opcodes = matcher.get_opcodes()
    assert isinstance(opcodes, list)
    assert matcher._opcodes is not None

def test_get_editops():
    matcher = StringMatcher(seq1="cat", seq2="cut")
    editops = matcher.get_editops()
    assert isinstance(editops, list)
    assert matcher._editops is not None

def test_get_matching_blocks():
    matcher = StringMatcher(seq1="banana", seq2="ana")
    blocks = matcher.get_matching_blocks()
    assert isinstance(blocks, list)
    assert matcher._matching_blocks is not None

def test_opcodes_from_editops_logic():
    matcher = StringMatcher(seq1="cat", seq2="cut")
    matcher.get_editops()
    opcodes = matcher.get_opcodes()
    assert opcodes is not None
    assert matcher._opcodes is not None

def test_editops_from_opcodes_logic():
    matcher = StringMatcher(seq1="cat", seq2="cut")
    matcher.get_opcodes()
    editops = matcher.get_editops()
    assert editops is not None
    assert matcher._editops is not None

def test_empty_strings():
    matcher = StringMatcher(seq1="", seq2="")
    assert matcher.ratio() == 1.0
    assert matcher.distance() == 3
    assert len(matcher.get_matching_blocks()) > 0