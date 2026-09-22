import pytest
import warnings
from StringMatcher import StringMatcher

def test_initialization():
    sm = StringMatcher(seq1="apple", seq2="pear")
    assert sm._str1 == "apple"
    assert sm._str2 == "pear"
    assert sm._ratio is None

def test_initialization_with_isjunk_warning():
    with pytest.warns(UserWarning, match="isjunk not NOT implemented"):
        StringMatcher(isjunk=lambda x: True, seq1="a", seq2="b")

def test_set_seqs():
    sm = StringMatcher()
    sm.set_seqs("test1", "test2")
    assert sm._str1 == "test1"
    assert sm._str2 == "test2"

def test_set_seq_methods_reset_cache():
    sm = StringMatcher("a", "b")
    sm.ratio()
    assert sm._ratio is not None
    
    sm.set_seq1("c")
    assert sm._ratio is None
    
    sm.ratio()
    sm.set_seq2("d")
    assert sm._ratio is None

def test_get_opcodes():
    sm = StringMatcher("book", "back")
    opcodes = sm.get_opcodes()
    assert isinstance(opcodes, list)
    # Verificamos que se cachea
    assert sm._opcodes is not None

def test_get_editops():
    sm = StringMatcher("book", "back")
    editops = sm.get_editops()
    assert isinstance(editops, list)
    assert sm._editops is not None

def test_get_matching_blocks():
    sm = StringMatcher("abc", "abc")
    blocks = sm.get_matching_blocks()
    assert len(blocks) > 0
    assert sm._matching_blocks is not None

def test_ratio_and_quick_ratio():
    sm = StringMatcher("test", "test")
    assert sm.ratio() == 1.0
    assert sm.quick_ratio() == 1.0

def test_real_quick_ratio():
    sm = StringMatcher("abc", "abcde")
    # 2.0 * min(3, 5) / (3 + 5) = 6 / 8 = 0.75
    assert sm.real_quick_ratio() == 0.75

def test_distance():
    sm = StringMatcher("kitten", "sitting")
    assert sm.distance() == 3
    assert sm._distance == 3

def test_cache_logic_opcodes_editops_interaction():
    # Prueba la lógica interna donde si existe editops, opcodes lo usa
    sm = StringMatcher("a", "b")
    editops = sm.get_editops()
    opcodes = sm.get_opcodes()
    assert sm._opcodes is not None
    assert sm._editops is not None

def test_empty_strings():
    sm = StringMatcher("", "")
    assert sm.ratio() == 1.0
    assert sm.distance() == 0
    assert len(sm.get_opcodes()) == 0