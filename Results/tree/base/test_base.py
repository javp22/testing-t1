import sys
from unittest.mock import MagicMock

# Mocks para dependencias externas ausentes
sys.modules["numpy"] = MagicMock()
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.stats"] = MagicMock()

sys.path.append("/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/tree")

from base import (
    f_entropy,
    information_gain,
    mse_criterion,
    xgb_criterion,
    get_split_mask,
    split,
    split_dataset,
)

def test_f_entropy():
    import numpy as np
    import scipy.stats as stats
    mock_p = MagicMock()
    mock_p.shape = (4,)
    np.bincount = MagicMock(return_value=np.array([2, 2]))
    stats.entropy = MagicMock(return_value=0.693147)
    assert f_entropy(mock_p) == 0.693147

def test_information_gain():
    y = MagicMock()
    y.shape = (4,)
    split_m = MagicMock()
    split_m.shape = (2,)
    gain = information_gain(y, [split_m, split_m])
    assert gain is not None

def test_mse_criterion():
    import numpy as np
    y = MagicMock()
    y.shape = (4,)
    split_m = MagicMock()
    split_m.shape = (2,)
    np.mean = MagicMock(return_value=2.0)
    np.sum = MagicMock(return_value=1.0)
    assert mse_criterion(y, [split_m, split_m]) == -1.0

def test_xgb_criterion():
    loss = MagicMock()
    loss.gain = MagicMock(return_value=1.0)
    y = {"actual": 0, "y_pred": 0}
    left = {"actual": 0, "y_pred": 0}
    right = {"actual": 0, "y_pred": 0}
    assert xgb_criterion(y, left, right, loss) == 1.0

def test_get_split_mask():
    import numpy as np
    X = MagicMock()
    X.__getitem__.return_value = np.array([1, 2])
    X.__getitem__.return_value.__lt__ = MagicMock(return_value=np.array([True, False]))
    X.__getitem__.return_value.__ge__ = MagicMock(return_value=np.array([False, True]))
    left, right = get_split_mask(X, 0, 1.5)
    assert left is not None
    assert right is not None

def test_split():
    import numpy as np
    X = MagicMock()
    X.__lt__ = MagicMock(return_value=np.array([True, False]))
    X.__ge__ = MagicMock(return_value=np.array([False, True]))
    y = MagicMock()
    y.__getitem__ = MagicMock(return_value=np.array([10]))
    left, right = split(X, y, 5)
    assert left is not None
    assert right is not None

def test_split_dataset():
    import numpy as np
    import base
    X = MagicMock()
    mask = np.array([True, False])
    target = {"a": MagicMock()}
    target["a"].__getitem__ = MagicMock(return_value=np.array([1]))
    base.get_split_mask = MagicMock(return_value=(mask, mask))
    left, right = split_dataset(X, target, 0, 5, return_X=False)
    assert "a" in left