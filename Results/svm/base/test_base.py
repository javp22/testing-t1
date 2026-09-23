import pytest
import numpy as np
from base import BaseEstimator

class ConcreteEstimator(BaseEstimator):
    def _predict(self, X=None):
        return X

def test_setup_input_basic():
    estimator = BaseEstimator()
    X = np.array([[1, 2], [3, 4]])
    y = np.array([0, 1])
    estimator._setup_input(X, y)
    assert np.array_equal(estimator.X, X)
    assert np.array_equal(estimator.y, y)
    assert estimator.n_samples == 2
    assert estimator.n_features == 2

def test_setup_input_list_conversion():
    estimator = BaseEstimator()
    X = [[1.0, 2.0]]
    y = [1]
    estimator._setup_input(X, y)
    assert isinstance(estimator.X, np.ndarray)
    assert isinstance(estimator.y, np.ndarray)
    assert np.array_equal(estimator.X, np.array([[1.0, 2.0]]))

def test_setup_input_empty_matrix_raises():
    estimator = BaseEstimator()
    with pytest.raises(ValueError, match="Got an empty matrix."):
        estimator._setup_input(np.array([]))

def test_setup_input_1d_array():
    estimator = BaseEstimator()
    X = np.array([1, 2, 3])
    y = np.array([1])
    estimator._setup_input(X, y)
    assert estimator.n_samples == 1
    assert estimator.n_features == (3,)

def test_setup_input_missing_y_raises():
    estimator = BaseEstimator()
    estimator.y_required = True
    with pytest.raises(ValueError, match="Missed required argument y"):
        estimator._setup_input(np.array([[1]]))

def test_setup_input_empty_y_raises():
    estimator = BaseEstimator()
    with pytest.raises(ValueError, match="The targets array must be no-empty."):
        estimator._setup_input(np.array([[1]]), np.array([]))

def test_fit():
    estimator = ConcreteEstimator()
    X = np.array([[1]])
    y = np.array([0])
    estimator.fit(X, y)
    assert np.array_equal(estimator.X, X)
    assert np.array_equal(estimator.y, y)

def test_predict_without_fit_raises():
    estimator = ConcreteEstimator()
    estimator.fit_required = True
    # BaseEstimator inicializa self.X = None hasta que se llama a fit
    with pytest.raises(ValueError, match="You must call `fit` before `predict`"):
        estimator.predict(np.array([[1]]))

def test_predict_success():
    estimator = ConcreteEstimator()
    X_fit = np.array([[1]])
    y_fit = np.array([0])
    X_test = np.array([[2]])
    estimator.fit(X_fit, y_fit)
    result = estimator.predict(X_test)
    assert np.array_equal(result, X_test)

def test_predict_no_fit_required():
    estimator = ConcreteEstimator()
    estimator.fit_required = False
    X = np.array([[5]])
    result = estimator.predict(X)
    assert np.array_equal(result, X)

def test_not_implemented_predict():
    class IncompleteEstimator(BaseEstimator):
        pass
    
    estimator = IncompleteEstimator()
    estimator.fit_required = False
    with pytest.raises(NotImplementedError):
        estimator.predict(np.array([[1]]))

def test_y_not_required():
    class NoYEstimator(BaseEstimator):
        y_required = False
        def _predict(self, X=None):
            return X
    
    estimator = NoYEstimator()
    X = np.array([[1]])
    estimator.fit(X)
    assert estimator.y is None