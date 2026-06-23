from typing import Tuple, Union
from os import PathLike

import numpy as np


def read_instance(
    path: Union[str, "PathLike[str]"],
) -> Tuple[np.ndarray, np.ndarray]:
    """Read a path-graph clustering instance from a CSV/text file.

    File format (as produced for the sanity-check instances):
      * one point per non-empty line, given as its comma-separated coordinates
        (a single value per line for the 1D case);
      * an empty line starts a new connected component;
      * the order of the lines encodes the order of the points along each path.

    Returns ``(X, component_ids)`` ready to pass to
    :meth:`PathCKC.fit`: ``X`` has shape ``(n_points, n_features)``
    and ``component_ids`` is the length-``n_points`` path-membership array.
    """
    coords = []
    component_ids = []
    component = 0
    seen_in_component = False

    with open(path, "r") as f:
        for line in f:
            stripped = line.strip()

            # Empty line -> boundary between components (ignore leading/repeated
            # blanks so they don't create empty components).
            if stripped == "":
                if seen_in_component:
                    component += 1
                    seen_in_component = False
                continue

            values = [v for v in stripped.replace(",", " ").split() if v]
            coords.append([float(v) for v in values])
            component_ids.append(component)
            seen_in_component = True

    if not coords:
        raise ValueError(f"No points found in instance file: {path}")

    n_features = len(coords[0])
    if any(len(row) != n_features for row in coords):
        raise ValueError(
            f"Inconsistent point dimensionality in instance file: {path}"
        )

    X = np.asarray(coords, dtype=np.float64)
    return X, np.asarray(component_ids, dtype=np.int32)
