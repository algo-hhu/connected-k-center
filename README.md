# Connected Path Graph Clustering

A library for algorithms for the connected k-center problem (as described in [1]). In this problem setting, the input consists of a point set $P$ and a desired number of centers $k$, along with a *connectivity graph* $G = (P,E)$. The goal is to partition $P$ into (at most) $k$ *clusters* $C_1, \ldots, C_k$, such that, for every $i$, the subgraph of $G$ induced by $C_i$ is connected.

As of now, only an algorithm for path graphs is implemented. A path graph is a graph whose connected components are simple paths. This algorithm was developed by Johanna Hillebrand and implemented by Julius Mann.


### References
[1] Drexler, L., Eube, J., Luo, K., Reineccius, D., Röglin, H., Schmidt, M., & Wargalla, J. (2024). Connected k-center and k-diameter clustering. Algorithmica, 86(11), 3425-3464.

## Installation

```bash
pip install connected_k_center
```

## Usage

The estimator expects a number $k$ of desired clusters and (optionally) a string that specifies the metric. Possible values are "rmse" (default), "euclidean" and "manhattan".

The fit method expects two arguments: A 2d numpy array of dimension $n\times d$ (where n is the number points and d the dimension they live in), and a numpy array of integers, specifying connected component IDs. If there is only one connected component, this argument can be omitted. 

```python
from connected_k_center import PathCKC

X = [
    [0., 1.,
    [1., 0.],
    [2., 1.],
    [1., 1.],
    [2., 0.],
    [3., 1.],
]

cids = [0,0,0,0,0,0]

pckc = PathCKC(n_clusters=2, metric="euclidean")
pckc.fit(X, cids)

print(pckc.optimal_radius_) # 1.4142135623730951
print(pckc.cluster_centers_indices_) # [1,5]
print(pckc.labels_) # [1,1,1,1,1,5]
```
## Development

Install [poetry](https://python-poetry.org/docs/#installation)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install clang
```bash
sudo apt-get install clang
```

Set clang variables
```bash
export CXX=/usr/bin/clang++
export CC=/usr/bin/clang
```

Install the package
```bash
poetry install
```

If the installation does not work and you do not see the C++ output, you can build the package to see the stack trace
```bash
poetry build
```

Run the tests
```bash
poetry run python -m unittest discover tests -v
```
