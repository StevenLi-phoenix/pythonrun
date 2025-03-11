import numpy as np


def test_basic_import():
    assert np.array([1, 2, 3]).sum() == 6


if __name__ == "__main__":
    test_basic_import()
