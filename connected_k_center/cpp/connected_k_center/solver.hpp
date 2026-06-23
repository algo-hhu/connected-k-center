#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/// Rückgabewert von connected_k_center() [Genutz für Ausgabe + Export].
    struct SolverResult {
        double optimal_radius = -1.0;            ///< -1.0 = keine Lösung gefunden
        std::vector<ComponentResult> components; ///< Ergebnis je Zusammenhangskomponente
    };

/**
 * Löst das Connected k-Center-Problem.
 *
 * Führt eine Binärsuche über alle paarweisen Distanzen durch und
 * bestimmt den minimalen Radius r*, für den eine Überdeckung mit
 * höchstens k Clustern möglich ist.
 *
 * @param k       Maximale Anzahl erlaubter Clusterzentren.
 * @param points  Eingabepunkte.
 * @param adj     Adjazenzliste (~> Graphstruktur).
 * @return        SolverResult mit optimalem Radius und Komponentenergebnissen.
 */
    SolverResult connected_k_center(int k, const std::vector<Point>& points, const AdjacencyList& adj, Metric metric = Metric::RMSE);

/**
 * Gibt das Ergebnis formatiert auf >>stdout<< aus.
 *
 * @param k               Parameter k.
 * @param result          Rückgabewert von connected_k_center().
 */
    void print_results(int k, const SolverResult& result);


 /**
 * Exportiert das Clustering-Ergebnis in eine CSV-Datei.
 *
 * Format:
 *   # k=<k>,optimal_radius=<r>,num_centers=<total>
 *   point_id,component_id,center_id
 *   0,1,2
 *   ...
 *
 * @param filepath  Zieldatei (überschrieben falls vorhanden).
 * @param k         Parameter k.
 * @param result    Rückgabewert von connected_k_center().
 * @return          true bei Erfolg, false bei Schreibfehler.
 */
    bool export_results_csv(
            const std::string& filepath,
            int k,
            const SolverResult& result
    );

} // namespace ckc