#include <Python.h>

#include <vector>

#include "connected_k_center/types.hpp"
#include "connected_k_center/solver.hpp"

typedef unsigned int uint;

// Build the list of ckc::Point from a flat, row-major coordinate array.
// Each point's id is its row index, matching the indexing used for the
// adjacency list and the output labels.
static std::vector<ckc::Point> array_to_points(const double *coords, uint n, uint d)
{
    std::vector<ckc::Point> points;
    points.reserve(n);
    for (uint i = 0; i < n; ++i)
    {
        ckc::Point p;
        p.id = static_cast<int>(i);
        p.coords.assign(coords + i * d, coords + i * d + d);
        points.push_back(std::move(p));
    }
    return points;
}

// Rebuild the path-graph adjacency from per-point component ids. Points that
// share a component id are chained in array order, reproducing the implicit
// path structure of the original CSV format (consecutive rows linked, a new
// component id starting a fresh path).
static ckc::AdjacencyList component_ids_to_adjacency(const int *component_ids, uint n)
{
    ckc::AdjacencyList adj(n);
    for (uint i = 1; i < n; ++i)
    {
        if (component_ids[i] == component_ids[i - 1])
        {
            adj[i].push_back(static_cast<int>(i - 1));
            adj[i - 1].push_back(static_cast<int>(i));
        }
    }
    return adj;
}

extern "C"
{
// "__declspec(dllexport)" causes the function to be exported when compiling on Windows.
// Otherwise the symbol is not exported and ctypes raises
//   "AttributeError: function 'connected_k_center_c' not found".
#if defined(_WIN32) || defined(__CYGWIN__)
    __declspec(dllexport)
#endif
    double
    connected_k_center_c(double *coords,        // input points, row-major (n x d)
                         int *component_ids,     // length n, path membership (array order = path order)
                         uint n,                 // number of points
                         uint d,                 // number of features
                         int k,                  // cluster budget (result uses at most k)
                         int *out_labels,        // length n, filled with the assigned center id per point
                         int *out_num_centers)   // scalar, filled with the total number of centers used
    {
        std::vector<ckc::Point> points = array_to_points(coords, n, d);
        ckc::AdjacencyList adj = component_ids_to_adjacency(component_ids, n);

        ckc::SolverResult result = ckc::connected_k_center(k, points, adj);

        // optimal_radius < 0 signals that no feasible clustering was found.
        if (result.optimal_radius < 0.0)
        {
            *out_num_centers = 0;
            return -1.0;
        }

        // Default to -1 so any point left unassigned is detectable on the Python side.
        for (uint i = 0; i < n; ++i)
        {
            out_labels[i] = -1;
        }

        int num_centers = 0;
        for (const auto &component : result.components)
        {
            num_centers += component.num_centers;
            for (const auto &assignment : component.assignments)
            {
                out_labels[assignment.point_id] = assignment.center_id;
            }
        }

        *out_num_centers = num_centers;
        return result.optimal_radius;
    }
} // extern "C"

static struct PyModuleDef _coremodule = {
    PyModuleDef_HEAD_INIT,
    "connected_k_center._core",
    NULL,
    -1,
    NULL,
};

PyMODINIT_FUNC PyInit__core(void)
{
    return PyModule_Create(&_coremodule);
}
