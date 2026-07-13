import io
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


class TestReadInstanceStream(unittest.TestCase):
    def test_stream_blank_line_starts_new_component(self) -> None:
        stream = io.StringIO("0.0\n1.0\n2.0\n\n10.0\n11.0\n12.0\n")
        X, comp = read_instance(stream)
        self.assertEqual(X.shape, (6, 1))
        np.testing.assert_array_equal(
            X.ravel(), np.array([0.0, 1.0, 2.0, 10.0, 11.0, 12.0])
        )
        np.testing.assert_array_equal(
            comp, np.array([0, 0, 0, 1, 1, 1], dtype=np.int32)
        )

    def test_stream_matches_file(self) -> None:
        # A stream and the equivalent on-disk file must parse identically.
        path = DATA_DIR / "tc5_two_components.csv"
        with open(path, "r") as f:
            content = f.read()

        X_file, comp_file = read_instance(path)
        X_stream, comp_stream = read_instance(io.StringIO(content))

        np.testing.assert_array_equal(X_file, X_stream)
        np.testing.assert_array_equal(comp_file, comp_stream)

    def test_stream_multi_feature(self) -> None:
        stream = io.StringIO("5,7\n6,6\n\n2,1\n3,1\n")
        X, comp = read_instance(stream)
        self.assertEqual(X.shape, (4, 2))
        np.testing.assert_array_equal(
            comp, np.array([0, 0, 1, 1], dtype=np.int32)
        )

    def test_stream_left_open_for_caller(self) -> None:
        # read_instance must not close a stream it did not open.
        stream = io.StringIO("1.0\n2.0\n")
        read_instance(stream)
        self.assertFalse(stream.closed)

    def test_empty_stream_raises(self) -> None:
        with self.assertRaises(ValueError):
            read_instance(io.StringIO("\n\n"))


if __name__ == "__main__":
    unittest.main()
