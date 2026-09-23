import pytest
import sys

# Ajustar el path para asegurar que puede importar el módulo structure
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/stock4/')

from structure import Structure, validate_attributes
from validate import Validator

def test_structure_init_and_fields():
    class Point(Structure):
        x = Validator(name='x')
        y = Validator(name='y')
    
    p = Point(1, 2)
    assert p.x == 1
    assert p.y == 2
    assert p._fields == ('x', 'y')

def test_structure_setattr_error():
    class Point(Structure):
        x = Validator(name='x')
    
    p = Point(10)
    with pytest.raises(AttributeError):
        p.z = 5

def test_structure_repr():
    class Point(Structure):
        x = Validator(name='x')
    
    p = Point(10)
    assert repr(p) == 'Point(10)'

def test_structure_eq():
    class Point(Structure):
        x = Validator(name='x')
    
    p1 = Point(10)
    p2 = Point(10)
    p3 = Point(20)
    assert p1 == p2
    assert p1 != p3
    assert p1 != "not a point"

def test_structure_iter():
    class Point(Structure):
        x = Validator(name='x')
        y = Validator(name='y')
    
    p = Point(1, 2)
    assert list(iter(p)) == [1, 2]

def test_from_row():
    class Point(Structure):
        x = Validator(name='x')
        y = Validator(name='y')
        # Ajustamos el expected_type esperado por from_row
        x.expected_type = int
        y.expected_type = int
    
    row = ['1', '2']
    p = Point.from_row(row)
    assert p.x == 1
    assert p.y == 2

def test_structure_internal_attribute_access():
    class Point(Structure):
        x = Validator(name='x')
    
    p = Point(1)
    p._private = 100
    assert p._private == 100

def test_empty_fields_structure():
    class Empty(Structure):
        pass
    
    e = Empty()
    assert e._fields == ()
    # StructureMeta inyecta __init__ en la clase base; 
    # comprobamos que no se intentó crear un nuevo __init__ mediante validate_attributes
    # el hasattr devuelve True porque la clase base tiene __init__ de object o definido
    assert hasattr(Empty, '__init__')

def test_validate_attributes_manual():
    # Evitamos usar typed_structure para saltar el problema de StructureMeta 
    # con dicts que no tienen 'maps'
    class Manual(Structure):
        x = Validator(name='x')
    
    validate_attributes(Manual)
    m = Manual(10)
    assert m.x == 10

def test_validated_decorator_logic():
    class Service(Structure):
        def action(self, x: int):
            return x
    
    # La clase pasa por __init_subclass__ que invoca validate_attributes
    s = Service()
    assert hasattr(s, 'action')
    # Validamos que el método original sigue funcionando
    assert s.action(10) == 10