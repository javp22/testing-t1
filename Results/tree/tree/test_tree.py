import sys
from unittest.mock import MagicMock, PropertyMock
import importlib.util
import pytest

# Mocking external dependencies
# We ensure that shapes and properties behave like integers for comparisons
np_mock = MagicMock()
# Setup shape return values for the test
shape_mock = PropertyMock(return_value=(20, 2))
type(np_mock.array.return_value).shape = shape_mock
sys.modules['numpy'] = np_mock
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.stats'] = MagicMock()
sys.modules['base'] = MagicMock()

# Load the target module
file_path = "/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/tree/tree.py"
spec = importlib.util.spec_from_file_location("tree", file_path)
tree_module = importlib.util.module_from_spec(spec)
sys.modules["tree"] = tree_module
spec.loader.exec_module(tree_module)

from tree import Tree

def test_initialization():
    t = Tree(regression=True, n_classes=3)
    assert t.regression is True
    assert t.n_classes == 3
    assert t.is_terminal is True

def test_is_terminal():
    t = Tree()
    assert t.is_terminal is True
    t.left_child = Tree()
    t.right_child = Tree()
    assert t.is_terminal is False

def test_calculate_leaf_value_regression():
    t = Tree(regression=True)
    targets = {"y": [10.0, 20.0]}
    np_mock.mean.return_value = 15.0
    t._calculate_leaf_value(targets)
    assert t.outcome == 15.0

def test_predict_row_terminal():
    t = Tree()
    t.outcome = 0.5
    assert t.predict_row([1, 2]) == 0.5

def test_predict_row_non_terminal():
    t = Tree()
    t.column_index = 0
    t.threshold = 5.0
    left = Tree()
    left.outcome = 1.0
    right = Tree()
    right.outcome = 2.0
    t.left_child = left
    t.right_child = right
    assert t.predict_row([3, 10]) == 1.0
    assert t.predict_row([6, 10]) == 2.0

def test_train_target_handling():
    t = Tree(regression=False)
    # Ensure np.unique returns a list/array with length 2
    np_mock.unique.return_value = [0, 1]
    
    # We use a mock that allows .shape[0] to be an int > 10 (min_samples_split default)
    X = MagicMock()
    X.shape = [15, 2]
    
    # Train with max_depth=0 to trigger early leaf creation via AssertionError
    t.train(X, {"y": [0, 1]}, max_depth=0)
    assert t.n_classes == 2