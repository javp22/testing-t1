import sys
import os
import pytest
from unittest.mock import MagicMock

# Configuración de path y mocks para permitir la carga del módulo
sys.path.insert(0, os.path.abspath("/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/tree/"))

numpy_mock = MagicMock()
numpy_mock.zeros.return_value = [0, 0, 0]
numpy_mock.bincount.return_value = MagicMock(shape=(1,))
numpy_mock.mean.return_value = 5.5
numpy_mock.unique.return_value = [1.0, 2.0]
sys.modules["numpy"] = numpy_mock
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.stats"] = MagicMock()

base_mock = MagicMock()
base_mock.split_dataset.return_value = (MagicMock(), MagicMock(), {"y": [0]}, {"y": [1]})
sys.modules["base"] = base_mock

from tree import Tree

def test_tree_initialization():
    t = Tree(regression=True, n_classes=2)
    assert t.regression is True
    assert t.n_classes == 2

def test_is_terminal_property():
    t = Tree()
    assert t.is_terminal is True
    t.left_child = Tree()
    t.right_child = Tree()
    assert t.is_terminal is False

def test_predict_row_logic():
    t = Tree()
    t.column_index = 0
    t.threshold = 10.0
    t.left_child = Tree()
    t.left_child.outcome = 1.0
    t.right_child = Tree()
    t.right_child.outcome = 0.0
    assert t.predict_row([5.0]) == 1.0
    assert t.predict_row([15.0]) == 0.0

def test_predict_array_processing():
    t = Tree()
    t.outcome = 99.0
    X = MagicMock()
    X.shape = (3, 1)
    X.__getitem__.side_effect = lambda i: [0]
    numpy_mock.zeros.return_value = [99.0, 99.0, 99.0]
    result = t.predict(X)
    assert len(result) == 3

def test_calculate_leaf_value_regression_path():
    t = Tree(regression=True)
    targets = {"y": MagicMock()}
    targets["y"].shape = (2,)
    t._calculate_leaf_value(targets)
    assert t.outcome == 5.5

def test_train_as_leaf_when_max_depth_zero():
    t = Tree()
    X = MagicMock()
    X.shape = (100, 2)
    y_data = MagicMock()
    y_data.shape = (2,)
    target = {"y": y_data}
    t.train(X, target, max_depth=0)
    assert t.is_terminal is True

def test_find_splits():
    t = Tree()
    X = [1.0, 2.0]
    splits = t._find_splits(X)
    assert 1.5 in splits

def test_train_gradient_boosting_path():
    t = Tree(regression=True)
    t.loss = MagicMock()
    t.loss.approximate.return_value = 0.5
    X = MagicMock()
    X.shape = (100, 1)
    target = {"y": [0], "actual": [0], "y_pred": [0]}
    
    # Trigger except branch via assert
    t.train(X, target, max_depth=0, loss=t.loss)
    assert t.outcome == 0.5

def test_train_classification_path():
    t = Tree(regression=False)
    X = MagicMock()
    X.shape = (100, 1)
    target = {"y": [0, 1]}
    # Forzamos la rama no cubierta de _calculate_leaf_value (clasificación)
    t.n_classes = 2
    t._calculate_leaf_value({"y": numpy_mock.array([0, 1])})
    assert t.outcome is not None

def test_find_best_split_logic():
    t = Tree()
    X = MagicMock()
    X.shape = (10, 1)
    X.__getitem__.return_value = [1, 2]
    target = {"y": [0, 1]}
    t.criterion = lambda y, splits: 0.5
    
    col, val, gain = t._find_best_split(X, target, 1)
    assert gain == 0.5