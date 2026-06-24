#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Determines all connected components (sub-paths) from the adjacency list.
 *
 * Each component is returned as an ordered path (vector of point IDs),
 * starting at an endpoint (degree 0 or 1).
 *
 * @param adj  Adjacency list of the graph.
 * @param n    Number of nodes.
 * @return     Vector of paths; each path is a vector of point IDs.
 */
    std::vector<std::vector<int>> extract_paths(const AdjacencyList& adj, int n);

} // namespace ckc