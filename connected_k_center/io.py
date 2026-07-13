from typing import Iterable, TextIO, Tuple, Union
from os import PathLike

import numpy as np


def _parse_lines(lines: Iterable[str], source: str) -> Tuple[np.ndarray, np.ndarray]:
    """Parse an iterable of text lines into ``(X, component_ids)``.

    ``source`` is only used to make error messages point at the offending input.
    """
    coords = []
    component_ids = []
    component = 0
    seen_in_component = False

    for line in lines:
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
        raise ValueError(f"No points found in instance: {source}")

    n_features = len(coords[0])
    if any(len(row) != n_features for row in coords):
        raise ValueError(f"Inconsistent point dimensionality in instance: {source}")

    X = np.asarray(coords, dtype=np.float64)
    return X, np.asarray(component_ids, dtype=np.int32)


def read_instance(
    source: Union[str, "PathLike[str]", TextIO],
) -> Tuple[np.ndarray, np.ndarray]:
    """Read a path-graph clustering instance from a CSV/text source.

    ``source`` may be either a filesystem path (``str``/``PathLike``) or an
    already-open text stream (any file-like object with a ``read`` method,
    e.g. an :class:`io.StringIO` or a Streamlit upload decoded to text).

    File format (as produced for the sanity-check instances):
      * one point per non-empty line, given as its comma-separated coordinates
        (a single value per line for the 1D case);
      * an empty line starts a new connected component;
      * the order of the lines encodes the order of the points along each path.

    Returns ``(X, component_ids)`` ready to pass to
    :meth:`PathCKC.fit`: ``X`` has shape ``(n_points, n_features)``
    and ``component_ids`` is the length-``n_points`` path-membership array.
    """
    # A str/PathLike is a filesystem path we open (and close) ourselves;
    # anything else is treated as an already-open text stream.
    if isinstance(source, (str, PathLike)):
        with open(source, "r") as f:
            return _parse_lines(f, source=str(source))

    return _parse_lines(source, source=getattr(source, "name", "<stream>"))
