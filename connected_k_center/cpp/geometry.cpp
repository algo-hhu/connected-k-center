#include "connected_k_center/geometry.hpp"

#include <cmath>
#include <algorithm>

namespace ckc {

// Distance function
double dist(const Point& a, const Point& b, Metric metric) {
    const int d = static_cast<int>(a.coords.size());
    if (d == 0) return 0.0;

    double sum = 0.0;

    switch(metric) {
        case Metric::RMSE:  //sqrt(mean of squares)
            for (int i = 0; i < d; ++i)
            {
                double diff = a.coords[i] - b.coords[i];
                sum += diff * diff;
            }
            return std::sqrt(sum / d);

        case Metric::Euclidean:    //standard Euclidean distance
            for (int i = 0; i < d; ++i)
             {
                double diff = a.coords[i] - b.coords[i];
                sum += diff * diff;
             }
             return std::sqrt(sum);

        case Metric::Manhattan: //Manhattan aka l_1 metric
            for (int i = 0; i < d; ++i)
            {
                sum += std::abs(a.coords[i] - b.coords[i]);
            }
            return sum;
    }
    return 0.0;

}


// Compute the sorted list of all distinct pairwise distances
std::vector<double> get_all_distances(const std::vector<Point>& points, Metric metric) {
    const int n = static_cast<int>(points.size());
    if (n < 2) return {0.0};

    // Pre-allocate (required for parallel writes)
    const int num_pairs = n * (n - 1) / 2;
    std::vector<double> distances(num_pairs + 1);
    distances[0] = 0.0;

    // Computation can be parallelized
    #pragma omp parallel for schedule(dynamic) default(none) shared(n, points, distances, metric)
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            int idx = 1 + i * n - (i * (i + 1)) / 2 + (j - i - 1);
            distances[idx] = dist(points[i], points[j], metric);
        }
    }

    // Remove duplicates
    std::sort(distances.begin(), distances.end());
    distances.erase(std::unique(distances.begin(), distances.end()), distances.end());
    return distances;
}

} // namespace ckc