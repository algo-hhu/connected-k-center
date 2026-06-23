#pragma once

#include <vector>
#include <boost/graph/adjacency_list.hpp>

namespace ckc {

/// Ein Punkt hat ID + mehrdimensionalen Koordinate
    struct Point {
        int id;
        std::vector<double> coords;
    };

/// Zuordnung: Punkt zu einem Clusterzentrum
    struct ClusterAssignment {
        int point_id;
        int center_id;
    };

/// Ergebnis des k-Center-Algorithmus für EINE Zusammenhangskomponente
    struct ComponentResult {
        bool feasible;
        int num_centers;
        std::vector<int> centers;
        std::vector<ClusterAssignment> assignments;
    };

/// Adjazenzliste: adj[i] ~> Nachbar-IDs von Punkt i
    using AdjacencyList = std::vector<std::vector<int>>;

/// Boost-Graph (ungerichtet)
    using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS>;

} // namespace ckc