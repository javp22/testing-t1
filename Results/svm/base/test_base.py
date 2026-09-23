import pytest
import sys
from unittest.mock import MagicMock

# Creamos una clase para simular el tipo ndarray de numpy
class MockNdarray:
    pass

sys.modules["numpy"] = MagicMock()
import numpy as np
np.ndarray = MockNdarray

sys.path.append("/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/svm")
from base import BaseEstimator

class ConcreteEstimator(BaseEstimator):
    def _predict(self, X=None):
        return X

class NoYRequiredEstimator(BaseEstimator):
    y_required = False
    def _predict(self, X=None):
        return X

def test_setup_input_valid_data():
    estimator = BaseEstimator()
    X = MockNdarray()
    X.size = 1
    X.ndim = 2
    X.shape = (2, 2)
    y = MockNdarray()
    y.size = 1
    
    estimator._setup_input(X, y)
    assert estimator.X == X
    assert estimator.y == y
    assert estimator.n_samples == 2

def test_setup_input_empty_matrix_raises():
    estimator = BaseEstimator()
    X = MockNdarray()
    X.size = 0
    with pytest.raises(ValueError, match="Got an empty matrix."):
        estimator._setup_input(X)

def test_setup_input_missing_y_raises():
    estimator = BaseEstimator()
    X = MockNdarray()
    X.size = 1
    X.ndim = 2
    X.shape = (1, 1)
    with pytest.raises(ValueError, match="Missed required argument y"):
        estimator._setup_input(X, None)

def test_fit_method():
    estimator = ConcreteEstimator()
    X = MockNdarray()
    X.size = 1
    X.ndim = 2
    X.shape = (1, 1)
    y = MockNdarray()
    y.size = 1
    estimator.fit(X, y)
    assert estimator.X == X

def test_predict_without_fit_raises():
    estimator = ConcreteEstimator()
    # Inicializar X como None explícitamente para el test
    estimator.X = None
    with pytest.raises(ValueError, match="You must call `fit` before `predict`"):
        estimator.predict(MockNdarray())

def test_no_y_required_estimator():
    estimator = NoYRequiredEstimator()
    X = MockNdarray()
    X.size = 1
    X.ndim = 2
    X.shape = (1, 1)
    estimator.fit(X)
    assert estimator.y is None
    estimator.predict(X)

def test_predict_not_implemented():
    estimator = BaseEstimator()
    estimator.fit_required = False
    # El atributo X no se inicializa solo, lo ponemos a None
    estimator.X = None
    # El método predict llama a _predict, que lanza NotImplementedError
    with pytest.raises(NotImplementedError):
        estimator.predict(MockNdarray())