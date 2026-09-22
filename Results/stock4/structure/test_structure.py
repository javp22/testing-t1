import sys
import pytest
from collections import ChainMap

# Asegurar que el directorio del archivo esté en el path
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/stock4')

from structure import Structure, validate_attributes
from validate import Validator

def create_validator(name, expected_type=None):
    v = Validator()
    v.name = name
    if expected_type:
        v.expected_type = expected_type
    return v

class User(Structure):
    name = create_validator('name', str)
    age = create_validator('age', int)

def test_structure_init_and_fields():
    user = User("Alice", 30)
    assert user.name == "Alice"
    assert user.age == 30
    assert user._fields == ('name', 'age')
    assert user._types == (str, int)

def test_structure_setattr_valid():
    user = User("Bob", 25)
    user.name = "Charlie"
    # El atributo privado debe poder ser seteado sin error
    user._internal = "hidden"
    assert user.name == "Charlie"
    assert user._internal == "hidden"

def test_structure_setattr_invalid():
    user = User("Bob", 25)
    with pytest.raises(AttributeError, match="No attribute invalid"):
        user.invalid = "fail"

def test_structure_repr():
    user = User("Alice", 30)
    assert repr(user) == "User('Alice', 30)"
    
    class Single(Structure):
        val = create_validator('val')
    s = Single(100)
    assert repr(s) == "Single(100)"

def test_structure_iter():
    user = User("Alice", 30)
    it = iter(user)
    assert next(it) == "Alice"
    assert next(it) == 30
    with pytest.raises(StopIteration):
        next(it)

def test_structure_eq():
    u1 = User("Alice", 30)
    u2 = User("Alice", 30)
    u3 = User("Bob", 25)
    u4 = User("Alice", 31)
    
    assert u1 == u2
    assert u1 != u3
    assert u1 != u4
    assert u1 != 123

def test_from_row():
    row = ("David", 40)
    # Prueba la conversión mediante _types
    user = User.from_row(row)
    assert user.name == "David"
    assert user.age == 40
    
    # Prueba conversión de tipos forzada por _types
    class Converter(Structure):
        val = create_validator('val', expected_type=float)
    c = Converter.from_row(['1.5'])
    assert c.val == 1.5

def test_structure_internal_meta():
    class Empty(Structure):
        pass
    empty = Empty()
    assert empty._fields == ()
    assert empty._types == ()
    # Verifica que el __prepare__ devuelva ChainMap
    assert isinstance(Empty.__prepare__("Empty", ()), ChainMap)

def test_validate_attributes_no_validators():
    # Verifica que el decorador trabaja con funciones anotadas
    class Processor(Structure):
        def compute(self, x: int) -> int:
            return x + 1
            
    obj = Processor()
    assert obj._fields == ()
    # validated() envuelve la función, verificamos que el wrapper funcione
    assert obj.compute(5) == 6
    assert hasattr(Processor.compute, "__wrapped__")

def test_create_init_logic():
    # Verifica que __init__ generado asigna los campos correctamente
    class Dynamic(Structure):
        f1 = create_validator('f1')
        f2 = create_validator('f2')
    
    d = Dynamic(10, 20)
    assert d.f1 == 10
    assert d.f2 == 20
    assert d._fields == ('f1', 'f2')
    
    # Verifica que los tipos son los esperados (identidad si no hay)
    assert d._types[0](5) == 5

def test_validate_attributes_order():
    # Verifica que _fields respeta el orden de definición
    class Ordered(Structure):
        b = create_validator('b')
        a = create_validator('a')
    
    o = Ordered(1, 2)
    assert o._fields == ('b', 'a')
    assert list(o) == [1, 2]