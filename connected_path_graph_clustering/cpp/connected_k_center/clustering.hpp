#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Berechnet die Radius-Membership für einen Pfad.
 *
 * M[i] enthält alle Zentren-IDs, die Punkt i bei Radius r
 * zusammenhängend (d.h. lückenlos auf dem Pfad) abdecken könnten.
 *
 * @param path    Geordneter Pfad als Vektor von Punkt-IDs.
 * @param points  Alle Punkte.
 * @param r       Suchradius.
 * @param n       Gesamtanzahl der Punkte.
 * @return        Membership-Vektor der Größe n.
 */
    std::vector<std::vector<int>> get_memberships_for_path(
            const std::vector<int>& path,
            const std::vector<Point>& points,
            double r,
            int n
    );

/**
 * Löst das 1D k-Center-Problem auf einem Pfad mittels Forward-DP.
 *
 * Findet die minimale Anzahl von Clustern, sodass jeder Punkt im Radius r
 * von seinem Zentrum liegt und das Zentrum im selben Intervall liegt.
 *
 * @param path_indices  Geordnete Punkt-IDs des Pfades.
 * @param M             Membership-Vektor aus get_memberships_for_path().
 * @param points        Alle Punkte.
 * @return              ComponentResult (Feasibility, Zentren und Zuordnungen).
 */
    ComponentResult solve_dp_forward(
            const std::vector<int>& path_indices,
            const std::vector<std::vector<int>>& M,
            const std::vector<Point>& points
    );

} // namespace ckc