from conans import ConanFile, CMake, tools
import os

class OpenimageioConan(ConanFile):
    name = "openvdb"
    version = "4.0.2"
    license = ""
    url = "https://github.com/dreamworksanimation/openvdb"
    requires = "blosc/1.11.2@pierousseau/stable", "glew/2.1.0@bincrafters/stable", "glfw/3.3@bincrafters/stable", "TBB/2019_U4@conan/stable", "zlib/1.2.11@conan/stable", "IlmBase/2.2.0@Mikayex/stable", "OpenEXR/2.2.0@pierousseau/stable","boost/1.70.0@conan/stable"
    description = "OpenVDB - Sparse volume data structure and tools http://www.openvdb.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False", "blosc:shared=False","OpenEXR:shared=False","IlmBase:shared=False","zlib:shared=False", "boost:shared=False", "boost:without_filesystem=False", "boost:without_regex=False", "boost:without_system=False", "boost:without_thread=False"
    generators = "cmake"

    def source(self):
        filename = "Release-%s.tar.gz" % self.version
        tools.download("https://github.com/dreamworksanimation/openvdb/archive/v%s.tar.gz" % self.version, filename)
        #from shutil import copyfile
        #copyfile("c:/tmp/"+filename, filename)
        tools.untargz(filename)
        os.unlink(filename)

        tools.replace_in_file("openvdb-%s/CMakeLists.txt" % self.version, 
            "PROJECT ( OpenVDB )",
            """PROJECT ( OpenVDB )
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set(BOOST_ROOT ${CONAN_BOOST_ROOT})
set(BOOST_LIBRARYDIR ${CONAN_BOOST_ROOT}/lib)
set(GLEW_LOCATION ${CONAN_GLEW_ROOT})
set(GLFW_LOCATION ${CONAN_GLFW_ROOT})
set(TBB_LOCATION ${CONAN_TBB_ROOT})
set(ILMBASE_LOCATION ${CONAN_ILMBASE_ROOT})
set(OPENVDB_BUILD_UNITTESTS OFF CACHE BOOL "unit tests")
set(OPENVDB_DISABLE_BOOST_IMPLICIT_LINKING OFF CACHE BOOL "")
set(Boost_IOSTREAMS_LIBRARY libboost_iostreams)
set(Boost_SYSTEM_LIBRARY libboost_system)
set(Boost_THREAD_LIBRARY libboost_thread)
set(Boost_PYTHON_LIBRARY libboost_python)
""")

        tools.replace_in_file("openvdb-%s/openvdb/CMakeLists.txt" % self.version,
            "COMPILE_FLAGS \"-DOPENVDB_PRIVATE -DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG}\"",
            "COMPILE_FLAGS \"-DOPENVDB_PRIVATE -DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG} $<$<CXX_COMPILER_ID:MSVC>:/bigobj>\"")
        tools.replace_in_file("openvdb-%s/openvdb/CMakeLists.txt" % self.version,
            "COMPILE_FLAGS \"-DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG}\"",
            "COMPILE_FLAGS \"-DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG} $<$<CXX_COMPILER_ID:MSVC>:/bigobj>\"")
        tools.replace_in_file("openvdb-%s/openvdb/CMakeLists.txt" % self.version,
            "COMPILE_FLAGS \"-DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG} -DGL_GLEXT_PROTOTYPES=1\"",
            "COMPILE_FLAGS \"-DOPENVDB_USE_BLOSC ${OPENVDB_USE_GLFW_FLAG} -DGL_GLEXT_PROTOTYPES=1 $<$<CXX_COMPILER_ID:MSVC>:/bigobj>\"")

        tools.replace_in_file("openvdb-%s/cmake/FindGLEW.cmake" % self.version,
            "FIND_LIBRARY ( GLEW_LIBRARY_PATH GLEW32 PATHS ${GLEW_LOCATION}/lib )",
            """FIND_LIBRARY ( GLEW_LIBRARY_PATH GLEW32D PATHS ${GLEW_LOCATION}/lib )
FIND_LIBRARY ( GLEW_LIBRARY_PATH GLEW32 PATHS ${GLEW_LOCATION}/lib )""")

        tools.replace_in_file("openvdb-%s/cmake/FindGLFW.cmake" % self.version,
            "SET( GLFW_glfw_LIBRARY ${GLFW_LIBRARY_PATH} CACHE STRING \"GLFW library\")",
            """SET( GLFW_glfw_LIBRARY ${GLFW_LIBRARY_PATH})""")

        tools.replace_in_file("openvdb-%s/cmake/FindGLFW.cmake" % self.version,
            "FIND_LIBRARY ( GLFW_LIBRARY_PATH glfw PATHS ${GLFW_LOCATION}/lib ${GLFW_LOCATION}/lib64",
            """FIND_LIBRARY ( GLFW_LIBRARY_PATH glfw3 PATHS ${GLFW_LOCATION}/lib ${GLFW_LOCATION}/lib64""")

        tools.replace_in_file("openvdb-%s/cmake/FindTBB.cmake" % self.version,
            "FIND_LIBRARY ( TBB_LIBRARY_PATH tbb PATHS ${TBB_LIBRARYDIR} PATH_SUFFIXES ${TBB_PATH_SUFFIXES}",
            """FIND_LIBRARY ( TBB_LIBRARY_PATH NAMES tbb tbb_debug PATHS ${TBB_LIBRARYDIR} PATH_SUFFIXES ${TBB_PATH_SUFFIXES}""")
        tools.replace_in_file("openvdb-%s/cmake/FindTBB.cmake" % self.version,
            "FIND_LIBRARY ( TBB_PREVIEW_LIBRARY_PATH tbb_preview PATHS ${TBB_LIBRARYDIR}  PATH_SUFFIXES ${TBB_PATH_SUFFIXES}",
            """FIND_LIBRARY ( TBB_PREVIEW_LIBRARY_PATH NAMES tbb_preview tbb_preview_debug PATHS ${TBB_LIBRARYDIR}  PATH_SUFFIXES ${TBB_PATH_SUFFIXES}""")
        tools.replace_in_file("openvdb-%s/cmake/FindTBB.cmake" % self.version,
            "FIND_LIBRARY ( TBBMALLOC_LIBRARY_PATH tbbmalloc PATHS ${TBB_LIBRARYDIR}  PATH_SUFFIXES ${TBB_PATH_SUFFIXES}",
            """FIND_LIBRARY ( TBBMALLOC_LIBRARY_PATH NAMES tbbmalloc tbbmalloc_debug PATHS ${TBB_LIBRARYDIR}  PATH_SUFFIXES ${TBB_PATH_SUFFIXES}""")

    def configure(self):
        if self.settings.os == "Windows" :
            self.options["TBB"].shared = True
        else :
            self.options["TBB"].shared = False

    def build(self):
        cmake = CMake(self)

        # Explicit way:
        self.run('cmake %s/openvdb-%s %s -DCMAKE_INSTALL_PREFIX="%s"' % (self.source_folder, self.version, cmake.command_line, self.package_folder))
        self.run("cmake --build . --target openvdb_static %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include/openvdb", src="openvdb-%s/openvdb"%self.version)
        self.copy("*.lib", dst="lib", keep_path=False)
        #self.copy("*.dll", dst="bin", keep_path=False)
        #self.copy("*.so", dst="lib", keep_path=False)
        #self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["libopenvdb"]
        self.cpp_info.defines = ["OPENVDB_STATICLIB","OPENVDB_OPENEXR_STATICLIB","OPENVDB_USE_BLOSC","OPENVDB_3_ABI_COMPATIBLE"]

# cmake C:\\Users\\pierre\\.conan\\data\\openvdb\\4.0.2\\hulud\\guerilla\\build\\8ba1feb74f0941c9756c4b137f7ec7c259af0c50/openvdb-4.0.2 -G "Visual Studio 14 2015 Win64" -DCONAN_LINK_RUNTIME="/MDd" -DCONAN_EXPORTED="1" -DCONAN_COMPILER="Visual Studio" -DCONAN_COMPILER_VERSION="14" -DBUILD_SHARED_LIBS="OFF" -DCMAKE_INSTALL_PREFIX="C:\\Users\\pierre\\.conan\\data\\openvdb\\4.0.2\\hulud\\guerilla\\package\\8ba1feb74f0941c9756c4b137f7ec7c259af0c50" -DCONAN_CXX_FLAGS="/MP40" -DCONAN_C_FLAGS="/MP40" -Wno-dev -DCMAKE_INSTALL_PREFIX="C:\\Users\\pierre\\.conan\\data\\openvdb\\4.0.2\\hulud\\guerilla\\package\\8ba1feb74f0941c9756c4b137f7ec7c259af0c50"        