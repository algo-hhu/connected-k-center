#pragma once

#include "types.hpp"
#include <vector>

namespace ckc {

/**
 * Ermittelt alle Zusammenhangskomponenten (Sub-Pfade) aus der Adjazenzliste.
 *
 * Jede Komponente wird als geordneter Pfad (Vektor von Punkt-IDs) zurückgegeben,
 * beginnend bei einem Endknoten (Grad 0 oder 1).
 *
 * @param adj  Adjazenzliste des Graphen.
 * @param n    Anzahl der Knoten.
 * @return     Vektor von Pfaden; jeder Pfad ist ein Vektor von Punkt-IDs.
 */
    std::vector<std::vector<int>> extract_paths(const AdjacencyList& adj, int n);

} // namespace ckc