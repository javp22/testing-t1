import sys
import os
import pytest

# Asegurar que el directorio del archivo objetivo esté en el path de importación
sys.path.insert(0, '/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/stock4/')

from validate import (
    Validator, Typed, Integer, Float, String, Positive, NonEmpty,
    PositiveInteger, PositiveFloat, NonEmptyString, validated, enforce
)

def test_validator_base():
    v = Validator("test")
    assert v.name == "test"
    assert v.check(10) == 10
    # Valida el registro __init_subclass__
    assert "Validator" in Validator.validators

def test_typed_validation():
    # Test valid types
    assert Integer.check(10) == 10
    assert Float.check(10.5) == 10.5
    assert String.check("hello") == "hello"
    
    # Test invalid types
    with pytest.raises(TypeError):
        Integer.check(10.5)
    with pytest.raises(TypeError):
        Float.check(1)
    with pytest.raises(TypeError):
        String.check(123)

def test_positive_validator():
    assert Positive.check(0) == 0
    assert Positive.check(10) == 10
    with pytest.raises(ValueError, match="must be >= 0"):
        Positive.check(-1)

def test_nonempty_validator():
    assert NonEmpty.check("abc") == "abc"
    with pytest.raises(ValueError, match="must be non-empty"):
        NonEmpty.check("")

def test_composite_validators():
    assert PositiveInteger.check(5) == 5
    assert PositiveFloat.check(5.5) == 5.5
    assert NonEmptyString.check("abc") == "abc"
    
    with pytest.raises(ValueError):
        PositiveInteger.check(-1)
    with pytest.raises(TypeError):
        PositiveInteger.check(1.5)
    with pytest.raises(ValueError):
        NonEmptyString.check("")

def test_validated_decorator():
    @validated
    def func(x: Integer, y: Positive):
        return x + y

    assert func(10, 5) == 15
    with pytest.raises(TypeError):
        func("a", -1)

def test_validated_return():
    @validated
    def func(x: Integer) -> Positive:
        return x

    assert func(10) == 10
    with pytest.raises(TypeError, match="Bad return"):
        func(-1)

def test_enforce_decorator():
    @enforce(x=Integer, y=Positive, return_=Integer)
    def func(x, y):
        return x + y

    assert func(10, 5) == 15
    with pytest.raises(TypeError):
        func(1.5, -1)

def test_descriptor_behavior():
    class Item:
        val = Integer()
        
    obj = Item()
    obj.val = 10
    assert obj.val == 10
    
    with pytest.raises(TypeError):
        obj.val = "not an int"

def test_validators_registry():
    assert "Integer" in Validator.validators
    assert "Positive" in Validator.validators
    assert "NonEmptyString" in Validator.validators