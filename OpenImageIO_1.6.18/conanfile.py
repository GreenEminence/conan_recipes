from conans import ConanFile, CMake, tools
import os

class OpenimageioConan(ConanFile):
    name = "OpenImageIO"
    version = "1.6.18"
    license = "Modified BSD License"
    url = "http://www.openimageio.org"
    requires = "boost/1.64.0@conan/stable", "IlmBase/2.2.0@pierousseau/stable", "libjpeg-turbo/1.5.2@pierousseau/stable", "libpng/1.6.37@bincrafters/stable", "libtiff/4.0.9@bincrafters/stable", "OpenEXR/2.2.0@pierousseau/stable", "zlib/1.2.11@conan/stable"
    description = "OpenImageIO http://www.openimageio.org"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False","IlmBase:shared=False", "zlib:shared=False", "OpenEXR:shared=False", "libpng:shared=False", "libjpeg-turbo:shared=False", "libtiff:shared=False", "boost:shared=False", "boost:without_filesystem=False", "boost:without_regex=False", "boost:without_system=False", "boost:without_thread=False"
    generators = "cmake"

    def source(self):
        filename = "Release-%s.tar.gz" % self.version
        tools.download("https://github.com/OpenImageIO/oiio/archive/Release-%s.tar.gz" % self.version, filename)
        #from shutil import copyfile
        #copyfile("c:/tmp/"+filename, filename)
        tools.untargz(filename)
        os.unlink(filename)

        if self.settings.os == "Windows" :
            libjpeg = "turbojpeg-static.lib"
            boost_libs = """
set(Boost_FILESYSTEM_LIBRARY boost_filesystem)
set(Boost_REGEX_LIBRARY boost_regex)
set(Boost_SYSTEM_LIBRARY boost_system)
set(Boost_THREAD_LIBRARY boost_thread)"""
        else :
            libjpeg = "libturbojpeg.a"
            boost_libs = """
set(Boost_FILESYSTEM_LIBRARY libboost_filesystem)
set(Boost_REGEX_LIBRARY libboost_regex)
set(Boost_SYSTEM_LIBRARY libboost_system)
set(Boost_THREAD_LIBRARY libboost_thread)"""
        
        tools.replace_in_file("oiio-Release-%s/CMakeLists.txt" % self.version, "project (OpenImageIO)",
                              """project (OpenImageIO)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set(ILMBASE_HOME ${CONAN_ILMBASE_ROOT})
set(BOOST_ROOT ${CONAN_BOOST_ROOT})
set(BOOST_LIBRARYDIR ${CONAN_BOOST_ROOT}/lib)
%s
set(OPENEXR_HOME ${CONAN_OPENEXR_ROOT})
find_package("ZLIB")
set(PNG_PNG_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_LIBPNG})
set(JPEG_LIBRARY ${CONAN_LIB_DIRS_LIBJPEG-TURBO}/%s)
""" % (boost_libs, libjpeg))
        
        # Remove -DOPENEXR_DLL
        tools.replace_in_file("oiio-Release-%s/CMakeLists.txt" % self.version, "add_definitions (-DOPENEXR_DLL)", "")

    def build(self):
        cmake = CMake(self)
        # cmake.configure(source_dir="%s/oiio-Release-%s" % (self.source_folder, self.version))
        # cmake.build()

        # Explicit way:
        self.run(('cmake %s/oiio-Release-%s %s -DBUILDSTATIC:BOOLEAN=ON -DLINKSTATIC:BOOLEAN=ON -DCMAKE_INSTALL_PREFIX="%s" -DSTOP_ON_WARNING=OFF') % (self.source_folder, self.version, cmake.command_line, self.package_folder))
        self.run("cmake --build . --target install %s -- -j20" % cmake.build_config)
        
    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["OpenImageIO"]
        self.cpp_info.defines = ["OIIO_STATIC_BUILD"]
