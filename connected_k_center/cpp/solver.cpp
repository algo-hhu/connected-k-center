#include "connected_k_center/solver.hpp"
#include "connected_k_center/geometry.hpp"
#include "connected_k_center/graph.hpp"
#include "connected_k_center/clustering.hpp"

#include <vector>

namespace ckc {

    /*///////////////////////////////////////////////////
    //////////////////// Overall logic //////////////////
    ///////////////////////////////////////////////////*/

    SolverResult connected_k_center(int k, const std::vector<Point>& points, const AdjacencyList& adj, Metric metric) {
        SolverResult result;
        const int n = static_cast<int>(points.size());
        if (n == 0) return result;

        /// [Step 0] Compute pairwise distances

        std::vector<double> distances = get_all_distances(points, metric);

        /// [Step 1] Build the graph and extract paths (connected components)
        Graph G(adj);
        std::vector<std::vector<int>> paths = G.extract_paths();

        /// [Step 2] Binary search over distances
        int low_idx  = 0;
        int high_idx = static_cast<int>(distances.size()) - 1;

        while (low_idx <= high_idx) {
            const int mid_idx = low_idx + (high_idx - low_idx) / 2;
            const double r = distances[mid_idx];

            int total_clusters = 0;
            bool possible = true;
            std::vector<ComponentResult> current_results;

            #pragma omp parallel for schedule(dynamic) default(none) shared(n, points, paths, r, possible, total_clusters, current_results, metric)
            for (const auto& path : paths) {

                auto M = get_memberships_for_path(path, points, r, n, metric);

                ComponentResult res = solve_dp_forward(path, M, points);

                if (!res.feasible) {
                    possible = false; // No valid clustering
                    // break;
                } else {
                    #pragma omp critical
                    {
                        total_clusters += res.num_centers;
                        current_results.push_back(res);
                    }
                }
            }

            if (possible && total_clusters <= k) {
                result.optimal_radius = r;
                result.components     = current_results;
                high_idx              = mid_idx - 1;
            } else {
                low_idx = mid_idx + 1;
            }
        }

        return result;
    }

} // namespace ckc