import sys
import os
import pytest

# Asegurar que el directorio del archivo fuente esté en el path
sys.path.insert(0, "/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/stock4")

from validate import (
    Validator, Integer, Float, String, Positive, NonEmpty, 
    PositiveInteger, PositiveFloat, NonEmptyString, 
    validated, enforce
)

def test_basic_validators_type_checks():
    assert Integer.check(10) == 10
    assert Float.check(10.5) == 10.5
    assert String.check("test") == "test"
    
    with pytest.raises(TypeError, match="expected <class 'int'>"):
        Integer.check("not an int")
    with pytest.raises(TypeError, match="expected <class 'float'>"):
        Float.check(1)
    with pytest.raises(TypeError, match="expected <class 'str'>"):
        String.check(123)

def test_compound_validators():
    assert PositiveInteger.check(5) == 5
    assert PositiveFloat.check(0.0) == 0.0
    assert NonEmptyString.check("a") == "a"
    
    with pytest.raises(ValueError, match="must be >= 0"):
        PositiveInteger.check(-1)
    with pytest.raises(ValueError, match="must be non-empty"):
        NonEmptyString.check("")

def test_descriptor_set():
    class TestContainer:
        x = Integer()
        
    obj = TestContainer()
    obj.x = 10
    assert obj.x == 10
    with pytest.raises(TypeError):
        obj.x = "string"

def test_validated_decorator():
    @validated
    def func(x: Integer, y: PositiveInteger) -> Integer:
        return x + y

    assert func(1, 2) == 3
    
    with pytest.raises(TypeError, match="Bad Arguments"):
        func("a", 1)
    
    @validated
    def bad_ret(x: Integer) -> PositiveInteger:
        return -5
    
    with pytest.raises(TypeError, match="Bad return"):
        bad_ret(1)

def test_enforce_decorator():
    @enforce(x=Integer, y=Positive, return_=Integer)
    def add(x, y):
        return x + y

    assert add(1, 5) == 6
    
    with pytest.raises(TypeError, match="Bad Arguments"):
        add(1, -1)
        
    @enforce(return_=Positive)
    def returns_neg():
        return -1
        
    with pytest.raises(TypeError, match="Bad return"):
        returns_neg()

def test_non_empty_edge_case():
    val = NonEmpty()
    assert val.check(" ") == " "
    with pytest.raises(ValueError, match="must be non-empty"):
        val.check("")

def test_validator_subclass_registry():
    assert "Integer" in Validator.validators
    assert "Positive" in Validator.validators
    assert "NonEmptyString" in Validator.validators

def test_enforce_no_return_check():
    @enforce(x=Integer)
    def identity(x):
        return x
    
    assert identity(10) == 10
    
    @enforce(x=Integer)
    def ret_neg(x):
        return -x
    assert ret_neg(10) == -10