#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Computes the distance between two points.
 * (e.g. root mean squared error over all coordinate dimensions)
 *
 * @return Distance, or 0.0 if a point has no coordinates.
 */
    double dist(const Point& a, const Point& b, Metric metric);

/**
 * Computes all pairwise distances between the given points.
 * The result is sorted and deduplicated.
 * The computation is (optionally) parallelized (OpenMP).
 *
 * @param points  Set of input points.
 * @param metric  Distance metric to use.
 * @return        Sorted, deduplicated vector of all pairwise distances.
 */
    std::vector<double> get_all_distances(const std::vector<Point>& points, Metric metric);

} // namespace ckc