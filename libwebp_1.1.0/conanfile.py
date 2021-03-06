import os
from conans import ConanFile, CMake, tools


class LibwebpConan(ConanFile):
    name = "libwebp"
    description = "Library to encode and decode images in WebP format"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/webmproject/libwebp"
    topics = ("image", "libwebp", "webp", "decoding", "encoding")
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False],
               "with_simd": [True, False], "near_lossless": [True, False],
               "swap_16bit_csp": [True, False]}
    default_options = {"shared": False, "fPIC": True,
                       "with_simd": True, "near_lossless": True,
                       "swap_16bit_csp": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _version_components(self):
        return [int(x) for x in self.version.split(".")]

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # should be an option but it doesn't work yet
        self._cmake.definitions["WEBP_ENABLE_SIMD"] = self.options.with_simd
        if self._version_components[0] >= 1:
            self._cmake.definitions["WEBP_NEAR_LOSSLESS"] = self.options.near_lossless
        else:
            self._cmake.definitions["WEBP_ENABLE_NEAR_LOSSLESS"] = self.options.near_lossless
        self._cmake.definitions["WEBP_ENABLE_SWAP_16BIT_CSP"] = self.options.swap_16bit_csp
        # avoid finding system libs
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GIF"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_TIFF"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = True
        self._cmake.definitions["WEBP_BUILD_ANIM_UTILS"] = False
        self._cmake.definitions["WEBP_BUILD_CWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_DWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_IMG2WEBP"] = False
        self._cmake.definitions["WEBP_BUILD_GIF2WEBP"] = False
        self._cmake.definitions["WEBP_BUILD_VWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_EXTRAS"] = False
        self._cmake.definitions["WEBP_BUILD_WEBPINFO"] = False
        self._cmake.definitions["WEBP_BUILD_WEBPMUX"] = False

        self._cmake.configure()

        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        # build libwebpmux (not in patch file to avoid one patch per version)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(WEBP_BUILD_GIF2WEBP OR WEBP_BUILD_IMG2WEBP)",
                              "if(TRUE)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["webpmux", "webpdemux", "webpdecoder", "webp"]
        if self.options.shared and self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.cpp_info.libs = [lib + ".dll" for lib in self.cpp_info.libs]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Linux" or self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        if self.options.shared:
            if self.settings.os == "Windows":
                self.env_info.PATH.append(os.path.join( self.package_folder, "bin"))
            else:
                self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
