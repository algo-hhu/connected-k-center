import unittest
from pathlib import Path

import numpy as np

from connected_k_center import read_instance

DATA_DIR = Path(__file__).parent / "data"


class TestReadInstance(unittest.TestCase):
    def test_single_point(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc1_single_point.csv")
        self.assertEqual(X.shape, (1, 1))
        self.assertEqual(X[0, 0], 5.0)
        np.testing.assert_array_equal(comp, np.array([0], dtype=np.int32))

    def test_single_component(self) -> None:
        # No blank line -> all points belong to one path/component.
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        self.assertEqual(X.shape, (6, 1))
        np.testing.assert_array_equal(comp, np.zeros(6, dtype=np.int32))

    def test_blank_line_starts_new_component(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc5_two_components.csv")
        self.assertEqual(X.shape, (6, 1))
        np.testing.assert_array_equal(
            comp, np.array([0, 0, 0, 1, 1, 1], dtype=np.int32)
        )

    def test_dtypes(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc2_close_chain.csv")
        self.assertEqual(X.dtype, np.float64)
        self.assertEqual(comp.dtype, np.int32)

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_instance(DATA_DIR / "does_not_exist.csv")


if __name__ == "__main__":
    unittest.main()
