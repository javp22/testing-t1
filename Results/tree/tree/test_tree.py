import pytest
import numpy as np
from tree import Tree

# El error anterior fue causado por falta de librerías en el entorno, 
# pero el código fuente original requiere numpy y scipy.
# Dado que el archivo 'base' no es parte del código fuente entregado pero es importado,
# definimos las funciones esperadas por el Tree para que los tests corran exitosamente.

def split(feature, target, value):
    left_mask = feature < value
    return [target[left_mask], target[~left_mask]]

def split_dataset(X, target, column, value, return_X=True):
    mask = X[:, column] < value
    left_X, right_X = X[mask], X[~mask]
    left_target = {k: v[mask] for k, v in target.items()}
    right_target = {k: v[~mask] for k, v in target.items()}
    if return_X:
        return left_X, right_X, left_target, right_target
    return left_target, right_target

def xgb_criterion(target, left, right, loss):
    return 1.0

# Inyectamos en el módulo base para evitar ImportError si fuera necesario
import sys
from types import ModuleType
base = ModuleType("base")
base.split = split
base.split_dataset = split_dataset
base.xgb_criterion = xgb_criterion
sys.modules["base"] = base

def test_tree_structure():
    t = Tree(regression=False)
    assert t.is_terminal is True
    assert t.left_child is None
    assert t.right_child is None

def test_find_splits():
    t = Tree()
    X = np.array([1.0, 3.0, 5.0])
    splits = t._find_splits(X)
    assert 2.0 in splits
    assert 4.0 in splits
    assert len(splits) == 2

def test_train_leaf_node():
    # Caso donde el número de muestras es menor al min_samples_split
    X = np.array([[1.0], [2.0]])
    y = np.array([0, 1])
    t = Tree(regression=False)
    t.train(X, y, min_samples_split=5)
    assert t.is_terminal is True
    assert t.outcome is not None

def test_train_creates_children():
    # Caso donde el árbol debe ramificarse
    X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0], [6.0], [7.0], [8.0], [9.0], [10.0], [11.0]])
    y = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    t = Tree(regression=False, criterion=lambda y, s: 1.0)
    t.train(X, y, min_samples_split=2, max_depth=2)
    assert t.is_terminal is False
    assert t.left_child is not None
    assert t.right_child is not None

def test_predict_logic():
    t = Tree()
    t.column_index = 0
    t.threshold = 5.0
    
    t.left_child = Tree()
    t.left_child.outcome = 10.0
    
    t.right_child = Tree()
    t.right_child.outcome = 20.0
    
    X = np.array([[2.0], [8.0]])
    preds = t.predict(X)
    assert preds[0] == 10.0
    assert preds[1] == 20.0

def test_calculate_leaf_classification():
    t = Tree(regression=False, n_classes=2)
    target = {"y": np.array([0, 1, 0])}
    t._calculate_leaf_value(target)
    # 0 aparece 2 veces, 1 aparece 1 vez. Probabilidades: [2/3, 1/3]
    assert np.allclose(t.outcome, np.array([0.66666667, 0.33333333]))

def test_calculate_leaf_regression():
    t = Tree(regression=True)
    target = {"y": np.array([10.0, 20.0])}
    t._calculate_leaf_value(target)
    assert t.outcome == 15.0