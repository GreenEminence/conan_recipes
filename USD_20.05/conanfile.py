import os
import shutil
from conans import ConanFile, CMake, tools

class USDConan(ConanFile):
    name = "USD"
    version = "20.05"
    license = ""
    url = "https://graphics.pixar.com/usd/docs/index.html"
    description = "Universal scene description"
    license = "Modified Apache 2.0 License"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "debug_symbols": [True, False]}
    default_options = "shared=True", "fPIC=True", "debug_symbols=False", "*:shared=False", "tbb:shared=True", "*:fPIC=True"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    short_paths = True
    _source_subfolder = "source_subfolder"

    def requirements(self):
        """Define runtime requirements."""

        # NOTE: python support is still not great in this version. Wait until the migration 
        # python 2 -> 3 is complete before building USD with python support.

        self.requires("Alembic/1.7.12@mercseng/version-0")
        self.requires("boost/1.73.0@mercseng/version-0")
        self.requires("hdf5/1.10.6@mercseng/version-0")
        self.requires("materialx/1.37.1@mercseng/version-0")
        self.requires("OpenColorIO/1.1.1@mercseng/version-0")
        self.requires("OpenImageIO/2.1.15.0@mercseng/version-0")
        self.requires("OpenSubdiv/3.4.3@mercseng/version-0")
        self.requires("tbb/2020.02@mercseng/version-0")
        self.requires("zlib/1.2.11@mercseng/version-0")
        self.requires("ptex/2.3.2@mercseng/version-0")


    def configure(self):
        # let boost use dependences we already built for other packages
        self.options["boost"].i18n_backend = "icu"
        self.options["boost"].zstd = True
        self.options["boost"].lzma = True


    def config_options(self):
        """fPIC is linux only."""
        if self.settings.os != "Linux":
            self.options.remove("fPIC")

    def source(self):
        """Retrieve source code."""
        tools.get("https://github.com/PixarAnimationStudios/USD/archive/v%s.tar.gz" % self.version)
        os.rename("USD-%s" % self.version, self._source_subfolder)
 
        # point to HDF5
        tools.replace_in_file("%s/CMakeLists.txt" % self._source_subfolder, "project(usd)",
                              """project(usd)

IF (DEFINED HDF5_ROOT)
    MESSAGE(STATUS "Using HDF5_ROOT: ${HDF5_ROOT}")
    # set HDF5_ROOT in the env so FindHDF5.cmake can find it
    SET(ENV{HDF5_ROOT} ${HDF5_ROOT})
ENDIF()
""")

        # Keeping this would mess up dllimport directives in MSVC
        tools.replace_in_file("%s/cmake/defaults/msvcdefaults.cmake" % self._source_subfolder, """_add_define("BOOST_ALL_DYN_LINK")""", "")
        # Nope, openEXR is not necessarily built as a dll. If it actually is, it will be added back by OpenEXR recipe anyway.
        tools.replace_in_file("%s/cmake/defaults/msvcdefaults.cmake" % self._source_subfolder, """_add_define("OPENEXR_DLL")""", "")
        # Alembic plugin needs to link against OpenExr Math library.
        tools.replace_in_file("%s/pxr/usd/plugin/usdAbc/CMakeLists.txt" % self._source_subfolder, """${OPENEXR_Half_LIBRARY}""", "${OPENEXR_Half_LIBRARY} ${OPENEXR_Imath_LIBRARY}")

        # Linux: Add flags -static-libgcc -static-libstdc++
        if self.settings.os == "Linux":
            tools.replace_in_file("%s/CMakeLists.txt" % self._source_subfolder,
            """set(CMAKE_CXX_FLAGS "${_PXR_CXX_FLAGS} ${CMAKE_CXX_FLAGS}")""", 
"""set(CMAKE_CXX_FLAGS "${_PXR_CXX_FLAGS} ${CMAKE_CXX_FLAGS}")
set(CMAKE_CXX_STANDARD_LIBRARIES "-static-libgcc -static-libstdc++ ${CMAKE_CXX_STANDARD_LIBRARIES}")
""")
        # Fix FindMaterialX
        tools.replace_in_file("%s/cmake/modules/FindMaterialX.cmake" % self._source_subfolder, """documents/Libraries""", """libraries/stdlib""")

        tools.replace_in_file(
            "%s/pxr/usd/ar/packageUtils.cpp" % self._source_subfolder,
            "#include \"pxr/pxr.h\"",
            """#include "pxr/pxr.h"
#include <algorithm>""")

        # Add a wrapper CMakeLists.txt file which initializes conan before executing the real CMakeLists.txt
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"), os.path.join(self._source_subfolder, "CMakeLists_original.txt"))
        shutil.copy("CMakeLists.txt", self._source_subfolder)

    def _configure_cmake(self):
        """Configure CMake."""
        cmake = CMake(self)

        if self.options.debug_symbols and self.settings.build_type=="Release":
            cmake.build_type = 'RelWithDebInfo'

        definition_dict = {
            "BUILD_SHARED_LIBS":self.options.shared,
            "PXR_BUILD_ALEMBIC_PLUGIN":True,
            "PXR_BUILD_DOCUMENTATION": False,
            "PXR_BUILD_DRACO_PLUGIN": False,
            "PXR_BUILD_EMBREE_PLUGIN": False,
            "PXR_BUILD_HOUDINI_PLUGIN": False,
            "PXR_BUILD_IMAGING":True,
            "PXR_BUILD_KATANA_PLUGIN": False,
            "PXR_BUILD_MATERIALX_PLUGIN":True,
            "PXR_BUILD_OPENCOLORIO_PLUGIN": True,
            "PXR_BUILD_OPENIMAGEIO_PLUGIN": True,
            "PXR_BUILD_PRMAN_PLUGIN": False,
            "PXR_BUILD_TESTS": False,
            "PXR_BUILD_USD_IMAGING": True,
            "PXR_BUILD_USDVIEW": False,
            "PXR_ENABLE_GL_SUPPORT": False,
            "PXR_ENABLE_HDF5_SUPPORT":True,
            "PXR_ENABLE_OPENVDB_SUPPORT": False,
            "PXR_ENABLE_OSL_SUPPORT":False,
            "PXR_ENABLE_PTEX_SUPPORT": True,
            "PXR_ENABLE_PYTHON_SUPPORT": False,
            "TBB_USE_DEBUG_BUILD": self.settings.build_type == "Debug",
            "HDF5_USE_STATIC_LIBRARIES": not self.options["hdf5"].shared
        }

        # Boost default find package is not great... give it a hand.
        #boost_libs = ['atomic', 'chrono', 'container', 'context', 'contract', 'coroutine', 'date_time', 'exception', 'fiber', 'filesystem', 'graph', 'graph_parallel', 'iostreams', 'locale', 'log', 'math', 'mpi', 'program_options', 'python', 'random', 'regex', 'serialization', 'stacktrace', 'system', 'test', 'thread', 'timer', 'type_erasure', 'wave']
        boost_libs = ['program_options']
        for searched_lib in boost_libs:
            for built_lib in self.deps_cpp_info["boost"].libs:
                if built_lib.find(searched_lib) != -1:
                    definition_dict["Boost_%s_FOUND" % searched_lib.upper()] = True
                    definition_dict["Boost_%s_LIBRARY" % searched_lib.upper()] = built_lib

        cmake.configure(defs = definition_dict, source_folder = self._source_subfolder)
        return cmake

    def build(self):
        """Build the elements to package."""
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        """Assemble the package."""
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.bindirs = ["lib", "bin"] # This will put "lib" folder in the path, which we need to find the plugins.
        self.cpp_info.defines = ["NOMINMAX", "YY_NO_UNISTD_H"]
        
        if self.settings.build_type == "Debug":
            self.cpp_info.defines.append("BUILD_OPTLEVEL_DEV")
        
        if not self.options.shared:
            self.cpp_info.defines.append("PXR_STATIC=1")
        if self.options.shared:
            if self.settings.os == "Windows":
                self.env_info.PATH.append(os.path.join( self.package_folder, "bin"))
            else:
                self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))