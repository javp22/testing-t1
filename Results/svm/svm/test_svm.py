import pytest
import numpy as np
from svm import SVM
from kernerls import Linear

@pytest.fixture
def sample_data():
    X = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [6.0, 5.0]])
    y = np.array([1.0, 1.0, -1.0, -1.0])
    return X, y

def test_svm_initialization():
    kernel = Linear()
    model = SVM(C=2.0, kernel=kernel, tol=1e-4, max_iter=200)
    assert model.C == 2.0
    assert model.kernel == kernel
    assert model.tol == 1e-4
    assert model.max_iter == 200
    assert model.b == 0

def test_svm_default_kernel():
    model = SVM()
    assert isinstance(model.kernel, Linear)

def test_fit_and_predict(sample_data):
    X, y = sample_data
    model = SVM(C=1.0)
    model.fit(X, y)
    
    predictions = model._predict(X)
    assert predictions.shape == (X.shape[0],)
    assert all(p in [-1.0, 1.0] for p in predictions)
    assert model.alpha is not None
    assert model.K.shape == (4, 4)

def test_clip():
    model = SVM()
    assert model.clip(5.0, 1.0, 0.0) == 1.0
    assert model.clip(-1.0, 1.0, 0.0) == 0.0
    assert model.clip(0.5, 1.0, 0.0) == 0.5

def test_find_bounds_different_labels():
    model = SVM(C=1.0)
    model.alpha = np.array([0.2, 0.3])
    model.y = np.array([1.0, -1.0])
    # i=0, y=1; j=1, y=-1
    L, H = model._find_bounds(0, 1)
    # L = max(0, 0.3 - 0.2) = 0.1
    # H = min(1.0, 1.0 - 0.2 + 0.3) = 1.0
    assert L == 0.1
    assert H == 1.0

def test_find_bounds_same_labels():
    model = SVM(C=1.0)
    model.alpha = np.array([0.2, 0.3])
    model.y = np.array([1.0, 1.0])
    # i=0, j=1
    L, H = model._find_bounds(0, 1)
    # L = max(0, 0.2 + 0.3 - 1.0) = 0
    # H = min(1.0, 0.2 + 0.3) = 0.5
    assert L == 0
    assert H == 0.5

def test_random_index():
    model = SVM()
    model.n_samples = 5
    for _ in range(10):
        idx = model.random_index(2)
        assert idx != 2
        assert 0 <= idx < 5

def test_error_calculation(sample_data):
    X, y = sample_data
    model = SVM()
    model.fit(X, y)
    err = model._error(0)
    # Predicted value using internal logic
    expected = model._predict_row(X[0]) - y[0]
    assert err == expected

def test_train_convergence(sample_data):
    X, y = sample_data
    model = SVM(max_iter=1)
    model.fit(X, y)
    # Verify alpha exists and internal structures were updated
    assert model.alpha is not None
    assert len(model.sv_idx) <= X.shape[0]

def test_predict_row_consistency(sample_data):
    X, y = sample_data
    model = SVM()
    model.fit(X, y)
    row_val = model._predict_row(X[0])
    assert isinstance(row_val, (float, np.float64))