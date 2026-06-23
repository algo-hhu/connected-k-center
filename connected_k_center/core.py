import ctypes
from typing import Any, Optional, Sequence

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.validation import validate_data

import connected_k_center._core  # type: ignore

_DLL = ctypes.cdll.LoadLibrary(connected_k_center._core.__file__)


class PathCKC(ClusterMixin, BaseEstimator):
    """Connected k-center clustering on path graphs.

    The algorithm performs a binary search over all pairwise distances and
    finds the minimum radius for which the points can be covered by at most
    ``n_clusters`` connected clusters. The graph is assumed to be a disjoint
    union of paths, supplied via ``component_ids``: points sharing a component
    id are linked, in the order in which they appear in ``X``, to form a path.

    This estimator is transductive -- it clusters a fixed, structured input and
    does not learn a reusable predictor -- so it only exposes ``fit`` /
    ``fit_predict`` and does not implement ``predict``, ``transform`` or
    ``score``.
    """

    def __init__(self, n_clusters: int = 8):
        self.n_clusters = n_clusters

    def fit(
        self,
        X: Sequence[Sequence[float]],
        y: Any = None,
        component_ids: Optional[Sequence[int]] = None,
    ) -> "PathCKC":
        self._validate_params()

        _X = validate_data(
            self,
            X,
            reset=True,
            accept_sparse=False,
            dtype=np.float64,
            order="C",
            accept_large_sparse=False,
        )
        assert isinstance(_X, np.ndarray), type(_X)
        _X = np.ascontiguousarray(_X)

        n_samples = _X.shape[0]
        self.n_features_in_ = _X.shape[1]

        if n_samples < self.n_clusters:
            raise ValueError(
                f"n_samples={n_samples} should be >= n_clusters={self.n_clusters}."
            )

        _component_ids = _validate_component_ids(component_ids, n_samples)

        # Declare c types
        c_coords = _X.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        c_component_ids = _component_ids.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        c_n = ctypes.c_uint(n_samples)
        c_d = ctypes.c_uint(self.n_features_in_)
        c_k = ctypes.c_int(self.n_clusters)

        labels = np.empty(n_samples, dtype=np.int32, order="C")
        c_labels = labels.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        c_num_centers = ctypes.c_int()

        _DLL.connected_k_center_c.argtypes = [
            ctypes.POINTER(ctypes.c_double),  # coords
            ctypes.POINTER(ctypes.c_int),  # component_ids
            ctypes.c_uint,  # n_samples
            ctypes.c_uint,  # n_features_in_
            ctypes.c_int,  # n_clusters (k)
            ctypes.POINTER(ctypes.c_int),  # labels
            ctypes.POINTER(ctypes.c_int),  # num_centers
        ]
        _DLL.connected_k_center_c.restype = ctypes.c_double

        radius = _DLL.connected_k_center_c(
            c_coords,
            c_component_ids,
            c_n,
            c_d,
            c_k,
            c_labels,
            ctypes.byref(c_num_centers),
        )

        if radius < 0:
            raise ValueError(
                f"No feasible connected clustering exists for n_clusters="
                f"{self.n_clusters}."
            )

        self.optimal_radius_ = radius
        self.labels_ = labels
        self.cluster_centers_indices_ = np.unique(labels)
        self.n_clusters_used_ = c_num_centers.value

        return self

    def fit_predict(
        self,
        X: Sequence[Sequence[float]],
        y: Any = None,
        component_ids: Optional[Sequence[int]] = None,
    ) -> np.ndarray:
        return self.fit(X, component_ids=component_ids).labels_

    def _validate_params(self) -> None:
        if not isinstance(self.n_clusters, (int, np.integer)):
            raise TypeError(
                f"n_clusters must be an integer, got {type(self.n_clusters).__name__}"
            )
        if self.n_clusters < 1:
            raise ValueError(f"n_clusters must be >= 1, got {self.n_clusters}")


def _validate_component_ids(
    component_ids: Optional[Sequence[int]],
    n_samples: int,
) -> np.ndarray:
    # Default: a single path over all points, in the given order.
    if component_ids is None:
        return np.zeros(n_samples, dtype=np.int32)

    ids = np.ascontiguousarray(component_ids, dtype=np.int32)
    if ids.ndim != 1:
        raise ValueError(f"component_ids must be 1D, got {ids.ndim}D")
    if ids.shape[0] != n_samples:
        raise ValueError(
            f"component_ids has length {ids.shape[0]}, expected {n_samples}."
        )
    return ids
