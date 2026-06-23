#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Berechnet den Abstand zwischen zwei Punkten.
 * (z.B. Root Mean Squared Error über alle Koordinatendimensionen)
 *
 * @return Distanz, oder 0.0 falls ein Punkt keine Koordinaten hat.
 */
    double dist(const Point& a, const Point& b, Metric metric);

/**
 * Berechnet alle paarweisen Distanzen zwischen den gegebenen Punkten.
 * Das Ergebnis ist sortiert und dedupliziert.
 * Die Berechnung wird (optional) parallelisiert (OpenMP).
 *
 * @param points  Menge der Eingabepunkte.
 * @return        Sortierter, deduplizierter Vektor aller paarweisen Distanzen.
 */
    std::vector<double> get_all_distances(const std::vector<Point>& points, Metric metric);

} // namespace ckc