import numpy as np


def test_basic_import():
    assert np.array([1, 2, 3]).sum() == 6


if __name__ == "__main__":
    print("np.array([1, 2, 3]).sum() = ", np.array([1, 2, 3]).sum())
    test_basic_import()
    print("测试完成")
