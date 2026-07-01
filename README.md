# Connected Path Graph Clustering

A library for algorithms for the connected k-center problem (as described in [1]). In this problem setting, the input consists of a point set $P$ and a desired number of centers $k$, along with a *connectivity graph* $G = (P,E)$. The goal is to partition $P$ into (at most) $k$ *clusters* $C_1, \ldots, C_k$, such that, for every $i$, the subgraph of $G$ induced by $C_i$ is connected.

As of now, only an algorithm for path graphs is implemented. A path graph is a graph whose connected components are simple paths. This algorithm was developed by Johanna Hillebrand (HHU).


### References
[1] Drexler, L., Eube, J., Luo, K., Reineccius, D., Röglin, H., Schmidt, M., & Wargalla, J. (2024). Connected k-center and k-diameter clustering. Algorithmica, 86(11), 3425-3464.
