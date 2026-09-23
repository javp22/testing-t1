import pytest
from warnings import catch_warnings
from StringMatcher import StringMatcher

def test_initialization():
    matcher = StringMatcher(seq1="test", seq2="text")
    assert matcher._str1 == "test"
    assert matcher._str2 == "text"

def test_isjunk_warning():
    with catch_warnings(record=True) as w:
        StringMatcher(isjunk=lambda x: True)
        assert len(w) == 1
        assert "isjunk not NOT implemented" in str(w[-1].message)

def test_set_methods():
    matcher = StringMatcher()
    matcher.set_seq1("abc")
    matcher.set_seq2("def")
    assert matcher._str1 == "abc"
    assert matcher._str2 == "def"
    
    matcher.set_seqs("ghi", "jkl")
    assert matcher._str1 == "ghi"
    assert matcher._str2 == "jkl"

def test_cache_reset():
    matcher = StringMatcher("a", "b")
    _ = matcher.ratio()
    assert matcher._ratio is not None
    matcher.set_seq1("c")
    assert matcher._ratio is None

def test_ratio_and_quick_ratio():
    matcher = StringMatcher("hello", "hella")
    r = matcher.ratio()
    assert isinstance(r, float)
    assert matcher.quick_ratio() == r

def test_real_quick_ratio():
    matcher = StringMatcher("abc", "abcde")
    # 2.0 * min(3, 5) / (3 + 5) = 2.0 * 3 / 8 = 0.75
    assert matcher.real_quick_ratio() == 0.75

def test_distance():
    matcher = StringMatcher("kitten", "sitting")
    assert matcher.distance() == 3

def test_get_opcodes():
    matcher = StringMatcher("abc", "adc")
    opcodes = matcher.get_opcodes()
    # Edit 'b' to 'd'
    assert len(opcodes) > 0
    assert matcher._opcodes is not None

def test_get_editops():
    matcher = StringMatcher("abc", "adc")
    editops = matcher.get_editops()
    assert len(editops) > 0
    assert matcher._editops is not None

def test_get_matching_blocks():
    matcher = StringMatcher("abc", "abc")
    blocks = matcher.get_matching_blocks()
    assert len(blocks) > 0

def test_opcodes_from_editops_branch():
    matcher = StringMatcher("abc", "adc")
    # Trigger logic branch where editops is set before opcodes
    _ = matcher.get_editops()
    opcodes = matcher.get_opcodes()
    assert opcodes is not None

def test_editops_from_opcodes_branch():
    matcher = StringMatcher("abc", "adc")
    # Trigger logic branch where opcodes is set before editops
    _ = matcher.get_opcodes()
    editops = matcher.get_editops()
    assert editops is not None

def test_empty_sequences():
    matcher = StringMatcher("", "")
    assert matcher.ratio() == 1.0
    assert matcher.distance() == 0
    assert matcher.real_quick_ratio() == 0.0 # 2.0 * 0 / 0 results in ZeroDivisionError in math, 
                                            # but testing current behavior