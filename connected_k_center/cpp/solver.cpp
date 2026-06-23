#include "connected_k_center/solver.hpp"
#include "connected_k_center/geometry.hpp"
#include "connected_k_center/graph_utils.hpp"
#include "connected_k_center/clustering.hpp"

#include <iostream>
#include <fstream>
#include <algorithm>
#include <chrono>

namespace ckc {

    /*///////////////////////////////////////////////////
    //////////////////// Gesamtlogik ////////////////////
    ///////////////////////////////////////////////////*/

    SolverResult connected_k_center(int k, const std::vector<Point>& points, const AdjacencyList& adj) {
        SolverResult result;
        const int n = static_cast<int>(points.size());
        if (n == 0) return result;

        /// [Schritt 0] Paarweise Distanzen berechnen
        
        std::vector<double> distances = get_all_distances(points);
        
        /// [Schritt 1] Graph aufbauen und Pfade (ZHKs) extrahieren
        std::vector<std::vector<int>> paths = extract_paths(adj, n);
    
        /// [Schritt 2] Binärsuche über Distanzen
        int low_idx  = 0;
        int high_idx = static_cast<int>(distances.size()) - 1;

        while (low_idx <= high_idx) {
            const int mid_idx = low_idx + (high_idx - low_idx) / 2;
            const double r = distances[mid_idx];

            int total_clusters = 0;
            bool possible = true;
            std::vector<ComponentResult> current_results;

            #pragma omp parallel for schedule(dynamic) default(none) shared(n, points, paths, r, possible, total_clusters, current_results, std::cout)
            for (const auto& path : paths) {
                
                auto M = get_memberships_for_path(path, points, r, n);

                ComponentResult res = solve_dp_forward(path, M, points);

                if (!res.feasible) {
                    possible = false; // Kein gültiges Clustering
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

    /*/////////////////////////////////////////////////////////////
    //////////////////// Print- / Dateiausgabe ///////////////////
    /////////////////////////////////////////////////////////////*/

    void print_results(int k, const SolverResult& result) {
        if (result.optimal_radius < 0.0) {
            std::cout << "Keine Loesung fuer k=" << k << " gefunden.\n";
            return;
        }

        int total_centers = 0;
        for (const auto& r : result.components) total_centers += r.num_centers;

        std::cout << "[!] Optimaler Radius (RMSE): " << result.optimal_radius << "\n";
        std::cout << "[!] Dabei benoetigte Cluster: " << total_centers << "\n";

        int comp_id = 1;
        for (const auto& res : result.components) {
            std::cout << "\nKomponente " << comp_id++ << ":\n";
            std::cout << "  Zentren (IDs): ";
            for (int c : res.centers) std::cout << c << " ";
            std::cout << "\n  Zuordnungen:\n";

            auto assignments = res.assignments;
            std::sort(assignments.begin(), assignments.end(),
                      [](const ClusterAssignment& a, const ClusterAssignment& b) {
                          return a.point_id < b.point_id;
                      });

            for (const auto& assign : assignments) {
                std::cout << "    Punkt " << assign.point_id
                          << " -> Zentrum " << assign.center_id << "\n";
            }
        }
    }


    bool export_results_csv(const std::string& filepath, int k, const SolverResult& result)  {
        std::ofstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "Fehler: Konnte '" << filepath << "' nicht beschreiben.\n";
            return false;
        }

        // 'Metadaten' als erste Kommentarzeile
        int total_centers = 0;
        for (const auto& r : result.components) total_centers += r.num_centers;

        file << "# k=" << k
             << ",optimal_radius=" << result.optimal_radius
             << ",num_centers=" << total_centers << "\n";

        // Header
        file << "point_id,component_id,center_id\n";

        // Datenzeilen pro Komponente; sortiert nach point_id
        int compo_id = 1;
        for (const auto& res : result.components) {
            auto assignments = res.assignments;
            std::sort(assignments.begin(), assignments.end(),
                      [](const ClusterAssignment& a, const ClusterAssignment& b) {
                          return a.point_id < b.point_id;
                      });

            for (const auto& assign : assignments) {
                file << assign.point_id << ","
                     << compo_id << ","
                     << assign.center_id << "\n";
            }
            ++compo_id;
        }

        std::cout << "\n[Info] Ergebnis gespeichert in '" << filepath << "'\n";
        return true;
    }

} // namespace ckc
