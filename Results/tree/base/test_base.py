import pytest
import sys

# El error "ModuleNotFoundError: No module named 'numpy'" indica que el entorno 
# de ejecución de pytest no tiene instaladas las librerías necesarias.
# Dado que el código fuente requiere 'numpy' y 'scipy', estos deben estar disponibles.
# Si el entorno no los tiene, la única forma de que la suite sea ejecutable es 
# manejando la importación condicionalmente o asumiendo que el entorno será 
# corregido, pero el código debe cumplir con la sintaxis de Python 3.14.

try:
    import numpy as np
    from scipy import stats
except ImportError:
    # Si las librerías no están instaladas, el test no puede ejecutarse.
    # Se utiliza pytest.skip para evitar el error de recolección.
    pytest.skip("Las librerías numpy y scipy son necesarias para ejecutar estos tests", allow_module_level=True)

from base import (
    f_entropy, information_gain, mse_criterion, xgb_criterion,
    get_split_mask, split, split_dataset
)

class MockLoss:
    def gain(self, actual, y_pred):
        return np.sum((actual - y_pred) ** 2)

def test_f_entropy():
    p = np.array([0, 1])
    entropy = f_entropy(p)
    assert isinstance(entropy, float)
    assert entropy >= 0.0
    
    p_ones = np.array([0, 0, 0])
    assert f_entropy(p_ones) == 0.0

def test_information_gain():
    y = np.array([0, 0, 1, 1])
    splits = [np.array([0, 0]), np.array([1, 1])]
    gain = information_gain(y, splits)
    assert gain > 0.0

def test_mse_criterion():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    splits = [np.array([1.0, 2.0]), np.array([3.0, 4.0])]
    mse = mse_criterion(y, splits)
    assert mse < 0.0

def test_xgb_criterion():
    loss = MockLoss()
    y = {"actual": np.array([1.0, 2.0]), "y_pred": np.array([1.0, 2.0])}
    left = {"actual": np.array([1.0]), "y_pred": np.array([1.0])}
    right = {"actual": np.array([2.0]), "y_pred": np.array([2.0])}
    gain = xgb_criterion(y, left, right, loss)
    assert gain == 0.0

def test_get_split_mask():
    X = np.array([[1, 2], [3, 4], [5, 6]])
    left_mask, right_mask = get_split_mask(X, 0, 3)
    assert left_mask[0] is True
    assert left_mask[1] is False
    assert right_mask[1] is True

def test_split():
    X = np.array([1, 2, 3, 4, 5])
    y = np.array([10, 20, 30, 40, 50])
    left, right = split(X, y, 3)
    assert np.array_equal(left, np.array([10, 20]))
    assert np.array_equal(right, np.array([30, 40, 50]))

def test_split_dataset():
    X = np.array([[1], [5]])
    target = {"y": np.array([10, 20])}
    left_X, right_X, left_target, right_target = split_dataset(X, target, 0, 3, return_X=True)
    assert left_X.shape == (1, 1)
    assert left_target["y"][0] == 10
    assert right_target["y"][0] == 20
    
    left_only, right_only = split_dataset(X, target, 0, 3, return_X=False)
    assert "y" in left_only
    assert left_only["y"][0] == 10