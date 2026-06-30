import sys
from typing import Any, Dict, List

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
        "connected_k_center/cpp/graph.cpp",
    ],

    include_dirs=["connected_k_center/cpp"],
)


class BuildExt(build_ext):
    """Compiler-aware build: select C++17 and OpenMP flags per toolchain.

    OpenMP parallelises the pairwise-distance and per-component computations.
    The way it is enabled differs by compiler:
      * GCC / Linux clang: ``-fopenmp`` for both compile and link.
      * Apple clang (macOS): ``-Xpreprocessor -fopenmp`` and link ``libomp``
        (its headers/libs come from Homebrew via CPPFLAGS/LDFLAGS).
      * MSVC (Windows): ``/openmp`` and ``/std:c++17`` (it ignores ``-std=``).
    """

    def build_extensions(self) -> None:
        if self.compiler.compiler_type == "msvc":
            compile_args = ["/std:c++17", "/openmp", "/EHsc"]
            link_args: List[str] = []
        elif sys.platform == "darwin":
            compile_args = ["-std=c++17", "-Xpreprocessor", "-fopenmp"]
            link_args = ["-lomp"]
        else:
            compile_args = ["-std=c++17", "-fopenmp"]
            link_args = ["-fopenmp"]

        for extension in self.extensions:
            extension.extra_compile_args = (
                list(extension.extra_compile_args) + compile_args
            )
            extension.extra_link_args = (
                list(extension.extra_link_args) + link_args
            )

        try:
            build_ext.build_extensions(self)
        except CompileError:
            # Workaround Issue #2.
            # '-stdlib=libc++' is added so the code can compile on macOS with
            # Anaconda. Irrelevant (and unsupported) for MSVC.
            if self.compiler.compiler_type == "msvc":
                raise
            for extension in self.extensions:
                extension.extra_compile_args.append("-stdlib=libc++")
                extension.extra_link_args.append("-stdlib=libc++")
            build_ext.build_extensions(self)


def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {"ext_modules": [extension], "cmdclass": {"build_ext": BuildExt}}
    )
