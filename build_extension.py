from typing import Any, Dict

from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools.errors import CompileError

extension = Extension(
    name="connected_k_center._core",
    sources=[
        "connected_k_center/_core.cpp",
        "connected_k_center/cpp/solver.cpp",
        "connected_k_center/cpp/clustering.cpp",
        "connected_k_center/cpp/geometry.cpp",
        "connected_k_center/cpp/graph_utils.cpp",
    ],
    # "cpp" is the include root so that #include "connected_k_center/<...>.hpp"
    # resolves to cpp/connected_k_center/. Boost.Graph is expected on the
    # default include path (e.g. /usr/include on Linux); add its location here
    # if it lives elsewhere.
    include_dirs=["connected_k_center/cpp"],
    # OpenMP parallelises the pairwise-distance and per-component computations.
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"],
)

# Thank you https://github.com/dstein64/kmeans1d!


class BuildExt(build_ext):
    """A custom build extension for adding -stdlib arguments for clang++."""

    def build_extensions(self) -> None:
        # '-std=c++17' is required for the structured bindings / std::filesystem
        # used by the algorithm. This works across compilers (ignored by MSVC).
        for extension in self.extensions:
            extension.extra_compile_args.append("-std=c++17")

        try:
            build_ext.build_extensions(self)
        except CompileError:
            # Workaround Issue #2.
            # '-stdlib=libc++' is added to `extra_compile_args` and `extra_link_args`
            # so the code can compile on macOS with Anaconda.
            for extension in self.extensions:
                extension.extra_compile_args.append("-stdlib=libc++")
                extension.extra_link_args.append("-stdlib=libc++")
            build_ext.build_extensions(self)


def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {"ext_modules": [extension], "cmdclass": {"build_ext": BuildExt}}
    )
