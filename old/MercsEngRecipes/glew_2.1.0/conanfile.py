import os
from conans import ConanFile, CMake, tools

class GlewConan(ConanFile):
    name = "glew"
    version = "2.1.0"
    description = "The GLEW library"
    url = "http://github.com/bincrafters/conan-glew"
    homepage = "http://github.com/nigels-com/glew"
    topics = ("conan", "glew", "opengl", "wrangler", "loader", "binding")
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindGLEW.cmake.in", "vs16-release-fix.patch"]
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    _source_subfolder = "_source_subfolder"

    #def requirements(self):
    #    """Define runtime requirements."""
    #    if self.settings.os == 'Linux':
    #        self.requires("mesa-glu/9.0.1@bincrafters/stable")

    def configure(self):
        """This is a C library. We don't care about CPP version."""
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        """fPIC is linux only."""
        if self.settings.os != 'Linux':
            self.options.remove("fPIC")

    def source(self):
        """Retrieve source code."""
        release_name = "%s-%s" % (self.name, self.version)
        tools.get("{0}/releases/download/{1}/{1}.tgz".format(self.homepage, release_name), sha256="04de91e7e6763039bc11940095cd9c7f880baba82196a7765f727ac05a993c95")
        os.rename(release_name, self._source_subfolder)
        
        # Fix build for Visual Studio 16 Release (issue #1087)
        tools.patch(base_path=self._source_subfolder, patch_file="vs16-release-fix.patch")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "BUILD_UTILS": False,
            "GLEW_REGAL": False,
            "GLEW_OSMESA": False,
            "CONAN_GLEW_DEFINITIONS": ";".join(self._glew_defines),
        }
        return definition_dict 

    def build(self):
        """Build the elements to package."""
        cmake = CMake(self)
        cmake.configure(defs = self.cmake_definitions())
        cmake.build()

    def package(self):
        """Assemble the package."""
        cmake = CMake(self)
        cmake.configure(defs = self.cmake_definitions())
        cmake.install()

        self.copy("FindGLEW.cmake", ".", ".", keep_path=False)
        self.copy("include/*", ".", "%s" % self._source_subfolder, keep_path=True)
        self.copy("%s/license*" % self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self.copy(pattern="*.pdb", dst="bin", keep_path=False)
                if self.options.shared:
                    if self.settings.build_type == "Release":
                        self.copy("glew32.lib", "lib", "lib", keep_path=False)
                        self.copy("glew32.dll", "bin", "bin", keep_path=False)
                    else:
                        self.copy("glew32d.lib", "lib", "lib", keep_path=False)
                        self.copy("glew32d.dll", "bin", "bin", keep_path=False)
                else:
                    if self.settings.build_type == "Release":
                        self.copy("libglew32.lib", "lib", "lib", keep_path=False)
                    else:
                        self.copy("libglew32d.lib", "lib", "lib", keep_path=False)
            else:
                if self.options.shared:
                    self.copy(pattern="*32.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*32d.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*32.a", dst="lib", keep_path=False)
                    self.copy(pattern="*32d.a", dst="lib", keep_path=False)
        elif self.settings.os == "Macos":
            if self.options.shared:
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                self.copy(pattern="*.so", dst="lib", keep_path=False)
                self.copy(pattern="*.so.*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    @property
    def _glew_defines(self):
        defines = []
        if self.settings.os == "Windows" and not self.options.shared:
            defines.append("GLEW_STATIC")
        return defines

    def package_info(self):
        """Edit package info."""
        self.cpp_info.defines = self._glew_defines
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']

            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.libs[0] = "lib" + self.cpp_info.libs[0]
                    self.cpp_info.libs.append("OpenGL32.lib")
            else:
                self.cpp_info.libs.append("opengl32")

        else:
            self.cpp_info.libs = ['GLEW']
            if self.settings.os == "Macos":
                self.cpp_info.frameworks = ["OpenGL"]

        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"
