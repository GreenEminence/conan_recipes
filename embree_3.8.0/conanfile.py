from conans import ConanFile, CMake, tools
import os

class EmbreeConan(ConanFile):
    name = "embree"
    version = "3.8.0"
    license = ""
    url = "embree.org"
    description = "High Performance Ray Tracing Kernels"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    requires = "TBB/2019_U6@pierousseau/stable"
    default_options = "shared=False", "fPIC=True", "TBB:shared=True"
    generators = "cmake"

    def configure(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        # https://github.com/embree/embree/archive/v3.8.0.tar.gz
        filename = "v%s.tar.gz" % self.version
        tools.download("https://github.com/embree/embree/archive/%s" % filename, filename)
        tools.untargz(filename)
        os.unlink(filename)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["EMBREE_TUTORIALS"] = False
        if ("fPIC" in self.options.fields and self.options.fPIC == True):
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True
        
        if self.settings.build_type == "Debug":
            cmake.definitions["EMBREE_TBB_ROOT"] = ""
            cmake.definitions["EMBREE_TBB_DEBUG_ROOT"] = self.deps_cpp_info["TBB"].rootpath
            cmake.definitions["EMBREE_TBB_DEBUG_POSTFIX"] = ""
        else:
            cmake.definitions["EMBREE_TBB_ROOT"] = self.deps_cpp_info["TBB"].rootpath
            cmake.definitions["EMBREE_TBB_DEBUG_ROOT"] = ""

        if self.options.shared:
            cmake.definitions["EMBREE_STATIC_LIB"] = True

        # Prevent compiler stack overflow: https://github.com/embree/embree/issues/157
        if self.settings.compiler == 'Visual Studio' and self.settings.compiler.version == 14 and self.settings.build_type == "Release":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-d2SSAOptimizer-"
        
        cmake.configure(source_dir="embree-%s" % self.version)
        cmake.build()

    def package(self):
        self.copy("*.h", src="embree-%s/" % self.version, dst="include/embree/")
        self.copy("*.lib", dst="lib/", keep_path=False)
        self.copy("*.a", dst="lib/", keep_path=False)
        if self.options.shared:
            self.copy("*.dll", dst="bin/", keep_path=False)
            self.copy("*.so", dst="bin/", keep_path=False)
            
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
