#include "connected_k_center/graph.hpp"

namespace ckc{

	void Graph::add_edge(int u, int v){
		adj[u].push_back(v);
		adj[v].push_back(u);
		degrees[u]++;
		degrees[v]++;
	}


	// Extract connected components as ordered paths
	std::vector<std::vector<int>> Graph::extract_paths() {

	    std::vector<std::vector<int>> paths;
	    std::vector<bool> visited(vertices.size(), false);

	    // Use path endpoints (degree 0 or 1) as start nodes
	    for (std::size_t i = 0; i < vertices.size(); ++i) {
	        if (!visited[i] && degrees[i] <= 1) {
	            std::vector<int> path;
	            int curr = i;
	            int prev = -1; // Predecessor node on the path

	            // Follow edges
	            while (curr != -1) {
	                path.push_back(curr);
	                visited[curr] = true;

	                int next = -1;
	                for (int nb : adj[curr]) {
					    if (nb != prev) {
					        next = nb;
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
}