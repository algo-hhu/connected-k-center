#pragma once

#include "types.hpp"
#include<numeric>
#include<vector>

namespace ckc{
	class Graph{
	public:

		std::vector<int> vertices;	// list of vertices
		std::vector<int> degrees;	// list of vertex degrees
		AdjacencyList adj;	// list of lists, where adj[i] contains all ids of neighbors of vertex i


		explicit Graph(int n): vertices(n), degrees(n,0), adj(n){			// constructor (creates graph with n vertices and no edges)
			std::iota(vertices.begin(), vertices.end(), 0);
		}

		Graph(AdjacencyList adjacency): vertices(adjacency.size()), degrees(adjacency.size()), adj(std::move(adjacency)){
			std::iota(vertices.begin(), vertices.end(), 0);
			for (std::size_t i = 0; i < adj.size(); ++i)
			{
				degrees[i] = static_cast<int>(adj[i].size());
			}
		}
		

		void add_edge(int u, int v);	//adds edge {u,v} to graph

		
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
	    std::vector<std::vector<int>> extract_paths();


	};
}