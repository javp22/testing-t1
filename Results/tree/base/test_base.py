import pytest
import numpy as np
from base import (
    f_entropy, 
    information_gain, 
    mse_criterion, 
    xgb_criterion, 
    get_split_mask, 
    split, 
    split_dataset
)

class MockLoss:
    def gain(self, actual, y_pred):
        return float(np.sum(actual - y_pred))

def test_f_entropy():
    # Caso normal
    p = np.array([0, 0, 1, 1])
    entropy = f_entropy(p)
    assert isinstance(entropy, float)
    
    # Caso borde: un solo valor, entropía 0
    p_single = np.array([1, 1, 1])
    assert f_entropy(p_single) == 0.0

def test_information_gain():
    y = np.array([0, 0, 1, 1])
    splits = [np.array([0, 0]), np.array([1, 1])]
    gain = information_gain(y, splits)
    # La entropía de [0,0,1,1] es ln(2), dividiendo perfectamente resulta en ganancia positiva
    assert gain > 0

def test_mse_criterion():
    y = np.array([1.0, 2.0, 3.0])
    splits = [np.array([1.0]), np.array([2.0, 3.0])]
    result = mse_criterion(y, splits)
    assert isinstance(result, float)
    # La suma de errores al cuadrado ponderada debe ser negativa según la implementación
    assert result <= 0

def test_xgb_criterion():
    loss = MockLoss()
    y = {"actual": np.array([1.0, 2.0]), "y_pred": np.array([0.5, 0.5])}
    left = {"actual": np.array([1.0]), "y_pred": np.array([0.5])}
    right = {"actual": np.array([2.0]), "y_pred": np.array([0.5])}
    
    gain = xgb_criterion(y, left, right, loss)
    # left_gain = 0.5, right_gain = 1.5, initial = 2.0. gain = 0.5 + 1.5 - 2.0 = 0
    assert gain == 0.0

def test_get_split_mask():
    X = np.array([[1, 2], [3, 4], [5, 6]])
    left, right = get_split_mask(X, 0, 3)
    assert left.tolist() == [True, False, False]
    assert right.tolist() == [False, True, True]

def test_split():
    X = np.array([1, 5, 2, 8])
    y = np.array([10, 50, 20, 80])
    left_y, right_y = split(X, y, 4)
    assert np.array_equal(left_y, np.array([10, 20]))
    assert np.array_equal(right_y, np.array([50, 80]))

def test_split_dataset_with_X():
    X = np.array([[1], [2], [3]])
    target = {"y": np.array([10, 20, 30])}
    left_X, right_X, left_t, right_t = split_dataset(X, target, 0, 2, return_X=True)
    
    assert left_X.shape[0] == 1
    assert right_X.shape[0] == 2
    assert left_t["y"][0] == 10
    assert right_t["y"].shape[0] == 2

def test_split_dataset_no_X():
    X = np.array([[1], [2], [3]])
    target = {"y": np.array([10, 20, 30])}
    left, right = split_dataset(X, target, 0, 2, return_X=False)
    
    assert "y" in left
    assert "y" in right
    assert len(left["y"]) == 1
    assert len(right["y"]) == 2