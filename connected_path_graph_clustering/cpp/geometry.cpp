#include "connected_k_center/geometry.hpp"

#include <cmath>
#include <algorithm>

namespace ckc {

// Distanzfunktion (RSME)
double dist(const Point& a, const Point& b) {
    const int d = static_cast<int>(a.coords.size());
    if (d == 0) return 0.0;

    double sum_squared = 0.0;
    for (int i = 0; i < d; ++i) {
        double diff = a.coords[i] - b.coords[i];
        sum_squared += diff * diff;
    }
    return std::sqrt(sum_squared / d);
}


// Sortierte Liste aller verschiedenen paarweisen Distanzen berechnen
std::vector<double> get_all_distances(const std::vector<Point>& points) {
    const int n = static_cast<int>(points.size());
    if (n < 2) return {0.0};

    // Vorab allokieren (notwendig für parallele Schreibzugriffe)
    const int num_pairs = n * (n - 1) / 2;
    std::vector<double> distances(num_pairs + 1);
    distances[0] = 0.0;

    // Berechnung kann parallelisiert werden
    #pragma omp parallel for schedule(dynamic) default(none) shared(n, points, distances)
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            int idx = 1 + i * n - (i * (i + 1)) / 2 + (j - i - 1);
            distances[idx] = dist(points[i], points[j]);
        }
    }

    // Duplikate entfernen
    std::sort(distances.begin(), distances.end());
    distances.erase(std::unique(distances.begin(), distances.end()), distances.end());
    return distances;
}

} // namespace ckc
