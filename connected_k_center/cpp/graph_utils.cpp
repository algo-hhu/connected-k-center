#include "connected_k_center/graph_utils.hpp"

#include <boost/graph/adjacency_list.hpp>

namespace ckc {

// Extract connected components as ordered paths
std::vector<std::vector<int>> extract_paths(const AdjacencyList& adj, int n) {
    Graph g(n);
    for (int u = 0; u < n; ++u) {
        for (int v : adj[u]) {
            if (u < v) {
                boost::add_edge(u, v, g);
            }
        }
    }

    std::vector<std::vector<int>> paths;
    std::vector<bool> visited(n, false);

    // Use path endpoints (degree 0 or 1) as start nodes
    for (int i = 0; i < n; ++i) {
        if (!visited[i] && boost::degree(i, g) <= 1) {
            std::vector<int> path;
            int curr = i;
            int prev = -1; // Predecessor node on the path

            // Follow edges
            while (curr != -1) {
                path.push_back(curr);
                visited[curr] = true;

                int next = -1;
                auto [nb_begin, nb_end] = boost::adjacent_vertices(curr, g);
                for (auto it = nb_begin; it != nb_end; ++it) {
                    if (static_cast<int>(*it) != prev) {
                        next = static_cast<int>(*it);
                        break; // In a path graph there is at most one such neighbor
                    }
                }

                prev = curr;
                curr = next;
            }
            paths.push_back(path);
        }
    }

    return paths;
}

} // namespace ckc