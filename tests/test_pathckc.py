import unittest
from pathlib import Path
import math

import numpy as np

from connected_k_center import PathCKC, read_instance

DATA_DIR = Path(__file__).parent / "data"


def _dist(a: np.ndarray, b: np.ndarray, metric: str) -> float:
    """Mirror of the C++ distance functions, for invariant checks."""
    diff = a - b
    if metric == "rmse":
        return float(np.sqrt(np.mean(diff**2)))
    if metric == "euclidean":
        return float(np.sqrt(np.sum(diff**2)))
    if metric == "manhattan":
        return float(np.sum(np.abs(diff)))
    raise ValueError(metric)


class TestPathCKCInvariants(unittest.TestCase):
    """Properties that must hold for any valid connected k-center solution."""

    INSTANCES = [
        ("tc2_close_chain.csv", 1),
        ("tc3_two_groups.csv", 2),
        ("tc5_two_components.csv", 2),
        ("tc6_asymmetric.csv", 1),
        ("tc7_three_groups_exact_k.csv", 3),
        ("tc8_coordinates_independent_path.csv", 3),
        ("tc9_2d_points.csv", 2),
    ]

    def test_invariants(self) -> None:
        for filename, k in self.INSTANCES:
            for metric in ("rmse", "euclidean", "manhattan"):
                with self.subTest(instance=filename, metric=metric):
                    X, comp = read_instance(DATA_DIR / filename)
                    model = PathCKC(n_clusters=k, metric=metric)
                    model.fit(X, component_ids=comp)

                    n = X.shape[0]
                    labels = model.labels_

                    # Every point is assigned to a real center.
                    self.assertEqual(labels.shape, (n,))
                    self.assertTrue(np.all(labels >= 0))

                    # At most n_clusters centers are used.
                    self.assertLessEqual(model.n_clusters_used_, k)
                    self.assertEqual(
                        model.n_clusters_used_, len(np.unique(labels))
                    )
                    np.testing.assert_array_equal(
                        model.cluster_centers_indices_, np.unique(labels)
                    )

                    # A center is assigned to itself.
                    for c in model.cluster_centers_indices_:
                        self.assertEqual(labels[c], c)

                    # k-center property: every point is within the radius.
                    self.assertGreaterEqual(model.optimal_radius_, 0.0)
                    for i in range(n):
                        d = _dist(X[i], X[labels[i]], metric)
                        self.assertLessEqual(d, model.optimal_radius_ + 1e-9)

                    # Connectivity: within a component, all points sharing a
                    # center form a contiguous run along the path.
                    self._assert_clusters_connected(labels, comp)

    def _assert_clusters_connected(
        self, labels: np.ndarray, comp: np.ndarray
    ) -> None:
        for component in np.unique(comp):
            idx = np.where(comp == component)[0]
            seen: set[int] = set()
            prev = None
            for i in idx:
                lab = int(labels[i])
                if lab != prev and prev is not None:
                    # Switching to a label we have already left is a break in
                    # contiguity -> the cluster would be disconnected.
                    self.assertNotIn(lab, seen, msg=f"cluster {lab} disconnected")
                if prev is not None:
                    seen.add(prev)
                prev = lab


class TestPathCKCKnownResults(unittest.TestCase):
    def test_close_chain_single_center(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc2_close_chain.csv")  # 0,1,2
        model = PathCKC(n_clusters=1).fit(X, component_ids=comp)
        self.assertEqual(model.optimal_radius_, 1.0)
        self.assertEqual(model.n_clusters_used_, 1)

    def test_two_groups_radius(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        model = PathCKC(n_clusters=2).fit(X, component_ids=comp)
        self.assertEqual(model.optimal_radius_, 1.0)
        self.assertEqual(model.n_clusters_used_, 2)

    def test_metric_equivalence_1d(self) -> None:
        # For 1-D data, rmse == euclidean == manhattan.
        X, comp = read_instance(DATA_DIR / "tc7_three_groups_exact_k.csv")
        radii = []
        for metric in ("rmse", "euclidean", "manhattan"):
            model = PathCKC(n_clusters=3, metric=metric).fit(
                X, component_ids=comp
            )
            radii.append(model.optimal_radius_)
        self.assertEqual(len(set(radii)), 1)

    def test_determinism(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        a = PathCKC(n_clusters=2).fit(X, component_ids=comp).labels_
        b = PathCKC(n_clusters=2).fit(X, component_ids=comp).labels_
        np.testing.assert_array_equal(a, b)

    def test_default_component_ids_single_path(self) -> None:
        # Without component_ids all points form one path, in input order.
        X, _ = read_instance(DATA_DIR / "tc3_two_groups.csv")
        model = PathCKC(n_clusters=2).fit(X)
        self.assertEqual(model.optimal_radius_, 1.0)

    def test_fit_predict_matches_labels(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        model = PathCKC(n_clusters=2)
        predicted = model.fit_predict(X, component_ids=comp)
        np.testing.assert_array_equal(predicted, model.labels_)


class TestPathCKCErrors(unittest.TestCase):
    def test_more_samples_required_than_clusters(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc1_single_point.csv")
        with self.assertRaises(ValueError):
            PathCKC(n_clusters=8).fit(X, component_ids=comp)

    def test_invalid_metric(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        with self.assertRaises(ValueError):
            PathCKC(n_clusters=1, metric="cosine").fit(X, component_ids=comp)

    def test_non_positive_n_clusters(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        with self.assertRaises(ValueError):
            PathCKC(n_clusters=0).fit(X, component_ids=comp)

    def test_non_integer_n_clusters(self) -> None:
        X, comp = read_instance(DATA_DIR / "tc3_two_groups.csv")
        with self.assertRaises(TypeError):
            PathCKC(n_clusters=2.5).fit(X, component_ids=comp)  # type: ignore[arg-type]

    def test_component_ids_wrong_length(self) -> None:
        X, _ = read_instance(DATA_DIR / "tc3_two_groups.csv")
        with self.assertRaises(ValueError):
            PathCKC(n_clusters=2).fit(X, component_ids=[0, 0, 0])

    def test_infeasible_more_components_than_clusters(self) -> None:
        # Two disconnected components cannot be covered by a single cluster.
        X, comp = read_instance(DATA_DIR / "tc5_two_components.csv")
        with self.assertRaises(ValueError):
            PathCKC(n_clusters=1).fit(X, component_ids=comp)

    def test_metrics_2d_data(self) -> None:
        # 2d coordinates, one connected component
        X, comp = read_instance(DATA_DIR / "tc9_2d_points.csv")

        # Check opt. solution value for RMSE metric
        model = PathCKC(n_clusters=2, metric="rmse").fit(X, component_ids=comp)
        self.assertAlmostEqual(model.optimal_radius_, 1)

        # Check opt. solution value for Euclidean metric
        model = PathCKC(n_clusters=2, metric="euclidean").fit(X, component_ids=comp)
        self.assertAlmostEqual(model.optimal_radius_, math.sqrt(2))

        # Check opt. solution value for Manhattan metric
        model = PathCKC(n_clusters=2, metric="manhattan").fit(X, component_ids=comp)
        self.assertEqual(model.optimal_radius_, 2)



if __name__ == "__main__":
    unittest.main()
