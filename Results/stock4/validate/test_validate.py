import sys
import os
import pytest

# Asegurar que el directorio del archivo fuente esté en el path para la importación
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/stock4')

from validate import (
    Validator, Integer, PositiveInteger, NonEmptyString,
    Positive, validated, enforce, isvalidator
)

class Model:
    x = Integer()
    y = PositiveInteger()
    s = NonEmptyString()

def test_validator_subclasses():
    # La clase Validator tiene el atributo 'validators'
    assert "Integer" in Validator.validators
    assert "Positive" in Validator.validators
    assert "NonEmptyString" in Validator.validators

def test_typed_validation():
    m = Model()
    m.x = 10
    assert m.x == 10
    # Al fallar isinstance(value, int), lanza TypeError: expected <class 'int'>
    with pytest.raises(TypeError, match="expected <class 'int'>"):
        m.x = "not an int"

def test_positive_validation():
    m = Model()
    m.y = 5
    assert m.y == 5
    with pytest.raises(ValueError, match="must be >= 0"):
        m.y = -1

def test_nonempty_validation():
    m = Model()
    m.s = "hello"
    assert m.s == "hello"
    with pytest.raises(ValueError, match="must be non-empty"):
        m.s = ""

def test_validated_decorator():
    @validated
    def add(a: Integer, b: Integer) -> Integer:
        return a + b

    assert add(1, 2) == 3
    # El decorador validated captura la excepción y añade prefijo "Bad Arguments"
    with pytest.raises(TypeError, match="Bad Arguments"):
        add(1, "two")

def test_validated_return_check():
    @validated
    def fail_return(a: Integer) -> Positive:
        return a

    # La validación del retorno ocurre después de la ejecución
    with pytest.raises(TypeError, match="Bad return"):
        fail_return(-1)

def test_enforce_decorator():
    @enforce(a=Integer, b=Positive, return_=Integer)
    def multiply(a, b):
        return a * b

    assert multiply(2, 3) == 6
    with pytest.raises(TypeError, match="Bad Arguments"):
        multiply("a", 3)
    with pytest.raises(TypeError, match="Bad Arguments"):
        multiply(2, -1)

def test_enforce_no_return_check():
    @enforce(a=Integer)
    def identity(a):
        return a

    assert identity(10) == 10

def test_validator_set():
    class TestValidator(Validator):
        @classmethod
        def check(cls, value):
            return value * 2
    
    t = TestValidator()
    instance = type('Instance', (), {})()
    t.__set_name__(None, 'attr')
    t.__set__(instance, 50)
    assert instance.__dict__['attr'] == 100

def test_isvalidator():
    assert isvalidator(Integer) is True
    assert isvalidator(int) is False
    assert isvalidator("String") is False