#include "connected_k_center/clustering.hpp"
#include "connected_k_center/geometry.hpp"

#include <algorithm>
#include <limits>
#include <iterator>

namespace ckc {

// Intersection of two SORTED vectors
static std::vector<int> intersect(const std::vector<int>& x, const std::vector<int>& y) {
    std::vector<int> result;
    std::set_intersection(x.begin(), x.end(), y.begin(), y.end(),
                          std::back_inserter(result));
    return result;
}

// Radius membership: M[i] = all centers that could cover point i within radius r *contiguously*
std::vector<std::vector<int>> get_memberships_for_path(const std::vector<int>& path, const std::vector<Point>& points, double r, int n, Metric metric) {
    std::vector<std::vector<int>> M(n);
    const int m = static_cast<int>(path.size());

    for (int center_idx = 0; center_idx < m; ++center_idx) {
        const int center_id = path[center_idx];

        // Extend to the left along the path
        for (int i = center_idx; i >= 0; --i) {
            const int target_id = path[i];
            if (dist(points[target_id], points[center_id], metric) <= r) {
                M[target_id].push_back(center_id);
            } else {
                break;
            }
        }

        // Extend to the right along the path
        for (int i = center_idx + 1; i < m; ++i) {
            const int target_id = path[i];
            if (dist(points[target_id], points[center_id], metric) <= r) {
                M[target_id].push_back(center_id);
            } else {
                break;
            }
        }
    }

    // Sort (precondition for intersect())
    for (int i = 0; i < n; ++i) {
        std::sort(M[i].begin(), M[i].end());
    }

    return M;
}


// Find the optimal clustering of a connected component
ComponentResult solve_dp_forward(const std::vector<int>& path_indices, const std::vector<std::vector<int>>& M, const std::vector<Point>& points) {
    const int n = static_cast<int>(path_indices.size());

    // Initialize DP matrix
    std::vector<int> dp_num_centers(n, std::numeric_limits<int>::max());

    // Avoid explicit backtracking; store results directly instead
    std::vector<std::vector<int>> partial_centers(n);
    std::vector<std::vector<ClusterAssignment>> partial_assignments(n);

    // Right interval boundary
    for (int i = 0; i < n; ++i) {
        std::vector<int> current_valid_centers;

        // Backward search for the (left) start point j of the 'current' cluster
        for (int j = i; j >= 0; --j) {
            const int u = path_indices[j];

            if (j == i) {
                current_valid_centers = M[u];
            } else {
                current_valid_centers = intersect(current_valid_centers, M[u]); // Only centers valid for ALL
            }

            if (current_valid_centers.empty()) break; // No suitable common center exists

            // Center must lie within the interval [j...i]
            int chosen_center = -1;
            for (int c : current_valid_centers) {
                for (int idx = j; idx <= i; ++idx) {
                    if (path_indices[idx] == c) {
                        chosen_center = c;
                        break;
                    }
                }
                if (chosen_center != -1) break; // Take the first valid one
            }

            // None of the centers lies WITHIN the interval
            if (chosen_center == -1) continue;

            // Combine the found cluster with those for [0,...,j-1]
            const int prev_num_centers = (j == 0) ? 0 : dp_num_centers[j - 1];
            if (prev_num_centers != std::numeric_limits<int>::max()) {
                if (prev_num_centers + 1 < dp_num_centers[i]) {
                    dp_num_centers[i] = prev_num_centers + 1; // Interval [j,...,i] has ONE additional cluster

                    if (j > 0) {
                        partial_centers[i]     = partial_centers[j - 1];
                        partial_assignments[i] = partial_assignments[j - 1];
                    } else {
                        partial_centers[i].clear();
                        partial_assignments[i].clear();
                    }

                    // Append the new center and the point assignments in the interval
                    partial_centers[i].push_back(points[chosen_center].id);
                    for (int idx = j; idx <= i; ++idx) {
                        partial_assignments[i].push_back(
                            {points[path_indices[idx]].id, points[chosen_center].id}
                        );
                    }
                }
            }
        }
    }

    // Build the ComponentResult if a solution exists
    ComponentResult result;
    if (dp_num_centers[n - 1] == std::numeric_limits<int>::max()) {
        result.feasible    = false;
        result.num_centers = 0;
    } else {
        result.feasible    = true;
        result.num_centers = dp_num_centers[n - 1];
        result.centers     = partial_centers[n - 1];
        result.assignments = partial_assignments[n - 1];
    }
    return result;
}

} // namespace ckc