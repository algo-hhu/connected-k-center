import ctypes
from typing import Optional, Sequence

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.validation import validate_data

import connected_k_center._core  # type: ignore

_DLL = ctypes.cdll.LoadLibrary(connected_k_center._core.__file__)

_METRIC_CODES = {
    "rmse": 0,
    "euclidean": 1,
    "manhattan": 2,
}  # for passing metric parameter down to c++


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
    ``score``. It also omits the sklearn ``y`` argument: there are no targets to
    ignore, and a CV split would reorder ``X`` and destroy the path structure
    that ``component_ids`` encodes, so the meta-estimator compatibility ``y``
    buys is not usable here anyway.

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Cluster index of each point, in ``0..n_clusters_used_ - 1``.
    cluster_centers_indices_ : ndarray of shape (n_clusters_used_,)
        Index into ``X`` of each cluster's center, so the center of point ``i``
        is ``X[cluster_centers_indices_[labels_[i]]]``.
    n_clusters_used_ : int
        Number of centers in the solution; at most ``n_clusters``.
    optimal_radius_ : float
        Smallest radius admitting a connected clustering with that many centers.
    """

    def __init__(self, n_clusters: int = 8, metric: str = "rmse"):
        self.n_clusters = n_clusters
        self.metric = metric

    def fit(
        self,
        X: Sequence[Sequence[float]],
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
        c_metric = ctypes.c_int(_METRIC_CODES[self.metric])

        labels = np.empty(n_samples, dtype=np.int32, order="C")
        c_labels = labels.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        c_num_centers = ctypes.c_int()

        _DLL.connected_k_center_c.argtypes = [
            ctypes.POINTER(ctypes.c_double),  # coords
            ctypes.POINTER(ctypes.c_int),  # component_ids
            ctypes.c_uint,  # n_samples
            ctypes.c_uint,  # n_features_in_
            ctypes.c_int,  # n_clusters (k)
            ctypes.c_int,  # metric
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
            c_metric,
            c_labels,
            ctypes.byref(c_num_centers),
        )

        if radius < 0:
            raise ValueError(
                f"No feasible connected clustering exists for n_clusters="
                f"{self.n_clusters}."
            )

        # The C++ side pre-fills the label array with -1 and overwrites it per
        # assignment, so a leftover -1 means a point was never assigned. The
        # relabelling below would silently turn that sentinel into cluster 0,
        # so it has to be caught here.
        if np.any(labels < 0):
            raise RuntimeError(
                f"{int(np.sum(labels < 0))} of {n_samples} points were left "
                f"unassigned by the solver."
            )

        # The solver labels each point with the *point index* of its center.
        # Expose that as cluster_centers_indices_ and renumber labels_ to
        # 0..n_clusters_used_-1, following sklearn's AffinityPropagation:
        # the center of point i is X[cluster_centers_indices_[labels_[i]]].
        center_indices, compact_labels = np.unique(labels, return_inverse=True)

        self.optimal_radius_ = radius
        self.labels_ = compact_labels.astype(np.int32, copy=False)
        self.cluster_centers_indices_ = center_indices
        self.cluster_centers_ = _X[center_indices]
        self.n_clusters_used_ = c_num_centers.value

        return self

    def fit_predict(
        self,
        X: Sequence[Sequence[float]],
        component_ids: Optional[Sequence[int]] = None,
    ) -> np.ndarray:
        return self.fit(X, component_ids).labels_

    def _validate_params(self) -> None:
        if not isinstance(self.n_clusters, (int, np.integer)):
            raise TypeError(
                f"n_clusters must be an integer, got {type(self.n_clusters).__name__}"
            )
        if self.n_clusters < 1:
            raise ValueError(f"n_clusters must be >= 1, got {self.n_clusters}")

        if self.metric not in _METRIC_CODES:
            raise ValueError(
                f"metric must be one of {sorted(_METRIC_CODES)}, got {self.metric!r}"
            )


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
