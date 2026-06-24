#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/// Return value of connected_k_center().
    struct SolverResult {
        double optimal_radius = -1.0;            ///< -1.0 = no solution found
        std::vector<ComponentResult> components; ///< result per connected component
    };

/**
 * Solves the connected k-center problem.
 *
 * Performs a binary search over all pairwise distances and determines the
 * minimum radius r* for which a covering with at most k clusters is possible.
 *
 * @param k       Maximum number of allowed cluster centers.
 * @param points  Input points.
 * @param adj     Adjacency list (i.e. graph structure).
 * @param metric  Distance metric to use.
 * @return        SolverResult with the optimal radius and per-component results.
 */
    SolverResult connected_k_center(int k, const std::vector<Point>& points, const AdjacencyList& adj, Metric metric = Metric::RMSE);

} // namespace ckc