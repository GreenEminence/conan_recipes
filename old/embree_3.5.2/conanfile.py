from conans import ConanFile, CMake, tools
import os

class EmbreeConan(ConanFile):
    name = "embree"
    version = "3.5.2"
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
        # https://github.com/embree/embree/archive/v3.5.2.tar.gz
        filename = "v%s.tar.gz" % self.version
        tools.download("https://github.com/embree/embree/archive/%s" % filename, filename)
        tools.untargz(filename)
        os.unlink(filename)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["EMBREE_TUTORIALS"] = False
        if ("fPIC" in self.options.fields and self.options.fPIC == True):
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True
        cmake.definitions["TBB_ROOT"] = self.deps_cpp_info["TBB"].rootpath
        cmake.configure(source_dir="embree-%s" % self.version)

        #cmake.build()
        cmake.build(target="math")
        cmake.build(target="simd")

    def package(self):
        self.copy("*.h", src="embree-%s/" % self.version, dst="include/embree/")
        if self.settings.os == "Windows":
            self.copy("*/math.lib", dst="lib/", keep_path=False)
            self.copy("*/simd.lib", dst="lib/", keep_path=False)
        else:
            self.copy("libmath.a", dst="lib/", keep_path=False)
            self.copy("libsimd.a", dst="lib/", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
