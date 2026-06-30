#pragma once

#include <vector>




namespace ckc {

    enum class Metric { RMSE = 0, Euclidean = 1, Manhattan = 2 };

/// A point has an ID + a multi-dimensional coordinate
    struct Point {
        int id;
        std::vector<double> coords;
    };

/// Assignment: point to a cluster center
    struct ClusterAssignment {
        int point_id;
        int center_id;
    };

/// Result of the k-center algorithm for ONE connected component
    struct ComponentResult {
        bool feasible;
        int num_centers;
        std::vector<int> centers;
        std::vector<ClusterAssignment> assignments;
    };

/// Adjacency list: adj[i] ~> neighbor IDs of point i
    using AdjacencyList = std::vector<std::vector<int>>;

} // namespace ckc