#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Computes the radius membership for a path.
 *
 * M[i] contains all center IDs that could cover point i at radius r
 * contiguously (i.e. with no gaps along the path).
 *
 * @param path    Ordered path as a vector of point IDs.
 * @param points  All points.
 * @param r       Search radius.
 * @param n       Total number of points.
 * @param metric  Distance metric to use.
 * @return        Membership vector of size n.
 */
    std::vector<std::vector<int>> get_memberships_for_path(
            const std::vector<int>& path,
            const std::vector<Point>& points,
            double r,
            int n,
            Metric metric
    );

/**
 * Solves the 1D k-center problem on a path via forward DP.
 *
 * Finds the minimum number of clusters such that every point lies within
 * radius r of its center and the center lies in the same interval.
 *
 * @param path_indices  Ordered point IDs of the path.
 * @param M             Membership vector from get_memberships_for_path().
 * @param points        All points.
 * @return              ComponentResult (feasibility, centers and assignments).
 */
    ComponentResult solve_dp_forward(
            const std::vector<int>& path_indices,
            const std::vector<std::vector<int>>& M,
            const std::vector<Point>& points
    );

} // namespace ckc