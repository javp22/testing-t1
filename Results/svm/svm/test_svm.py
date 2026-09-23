import pytest
import numpy as np
from svm import SVM
from kernerls import Linear

@pytest.fixture
def sample_data():
    X = np.array([[1, 2], [2, 3], [3, 3], [2, 1], [3, 2]])
    y = np.array([1, 1, 1, -1, -1])
    return X, y

def test_svm_initialization():
    kernel = Linear()
    model = SVM(C=2.0, kernel=kernel, tol=1e-4, max_iter=50)
    assert model.C == 2.0
    assert model.kernel == kernel
    assert model.tol == 1e-4
    assert model.max_iter == 50
    assert model.b == 0
    assert model.alpha is None

def test_svm_default_initialization():
    model = SVM()
    assert isinstance(model.kernel, Linear)
    assert model.C == 1.0

def test_svm_fit_and_predict(sample_data):
    X, y = sample_data
    model = SVM(max_iter=10)
    model.fit(X, y)
    
    assert model.alpha is not None
    assert len(model.alpha) == len(y)
    
    predictions = model._predict(X)
    assert predictions.shape == (len(y),)
    # Check if predictions are only 1 or -1
    assert np.all(np.isin(predictions, [-1, 1]))

def test_svm_clip():
    model = SVM()
    assert model.clip(10, 5, 0) == 5
    assert model.clip(-1, 5, 0) == 0
    assert model.clip(2, 5, 0) == 2

def test_svm_find_bounds_different_classes():
    model = SVM(C=1.0)
    model.alpha = np.array([0.5, 0.5])
    model.y = np.array([1, -1])
    # Case y[i] != y[j]
    L, H = model._find_bounds(0, 1)
    # L = max(0, 0.5 - 0.5) = 0
    # H = min(1, 1 - 0.5 + 0.5) = 1
    assert L == 0
    assert H == 1

def test_svm_find_bounds_same_classes():
    model = SVM(C=1.0)
    model.alpha = np.array([0.2, 0.2])
    model.y = np.array([1, 1])
    # Case y[i] == y[j]
    L, H = model._find_bounds(0, 1)
    # L = max(0, 0.2 + 0.2 - 1) = 0
    # H = min(1, 0.2 + 0.2) = 0.4
    assert L == 0
    assert H == 0.4

def test_svm_random_index():
    model = SVM()
    model.n_samples = 5
    idx = model.random_index(0)
    assert idx != 0
    assert 0 <= idx < 5

def test_error_method(sample_data):
    X, y = sample_data
    model = SVM()
    model.fit(X, y)
    err = model._error(0)
    assert isinstance(err, float)
    
def test_predict_row_consistency(sample_data):
    X, y = sample_data
    model = SVM()
    model.fit(X, y)
    val = model._predict_row(X[0])
    assert isinstance(val, (float, np.float64))

def test_convergence_behavior(sample_data):
    X, y = sample_data
    # Low max_iter to test loop termination
    model = SVM(max_iter=1)
    model.fit(X, y)
    assert model.alpha is not None