import os, sys
from distutils.dir_util import copy_tree
from conans import ConanFile, tools

class PySide2(ConanFile):
    name = "PySide2"
    version = "5.13.2"
    description = "Qt for Python"
    license = "LGPL-3.0"
    url = "https://doc.qt.io/qtforpython"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    _source_subfolder = "source_subfolder"
    short_paths = True


    def build_requirements(self):
        """Define buid toolset."""
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom_installer/1.1.2@bincrafters/stable")
        self.build_requires("cpython/3.7.7@mercseng/stable")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("qt/5.12.6@mercseng/stable")
        self.requires("OpenSSL/1.1.1c@conan/stable")
        self.requires("libxml2/2.9.9@pierousseau/stable")
        if self.settings.os == "Windows":
            self.requires("libclang/7.0@mercseng/stable")

    def config_options(self):
        """fPIC is linux only."""
        if self.settings.os != "Linux":
            self.options.remove("fPIC")

    def configure(self):
        if self.settings.os == "Windows":
            self.options["qt"].opengl = "dynamic"

        self.options["qt"].qtsvg = True
        self.options["qt"].qtdoc = True
        self.options["qt"].qtxmlpatterns = True

        self.options["qt"].openssl = False
        self.options["qt"].with_openal = False
        self.options["qt"].with_freetype = True
        self.options["qt"].with_harfbuzz = True
        self.options["qt"].with_glib = False
        self.options["qt"].with_mysql = False
        self.options["qt"].with_pq = False
        self.options["qt"].with_libpng = True
        self.options["qt"].with_odbc = False
        
        self.options["qt"].shared = True
    
    def source(self):
        """Retrieve source code."""        
        tools.get("https://download.qt.io/official_releases/QtForPython/pyside2/PySide2-%s-src/pyside-setup-opensource-src-%s.zip" % (self.version, self.version))
        os.rename("pyside-setup-opensource-src-%s" % self.version, self._source_subfolder)

    def build(self):
        """Build the elements to package."""        
        qmake = "qmake"

        environment = {}
        if self.settings.os == "Windows":
            environment = tools.vcvars_dict(self)
            environment["CMAKE_GENERATOR"] = "Visual Studio 14 2015 Win64"
            qmake += ".exe"

        environment["PYSIDE_DISABLE_INTERNAL_QT_CONF"] = "1"

        # There may be a DLL conflict. Put Qt and libClang DLLs in front of the PATH.
        if self.settings.os == "Windows":
            if not "PATH" in environment:
                environment["PATH"] = []
            environment["PATH"].insert(0, self.deps_cpp_info["qt"].bin_paths[0])
            environment["PATH"].insert(0, self.deps_cpp_info["libclang"].bin_paths[0])
        
        arguments = [
            "--qmake=\"%s\"" % os.path.join(self.deps_cpp_info["qt"].rootpath, "bin", qmake),
            "--skip-modules=QtNetwork,QtOpenGLFunctions,QtQuick,QtQuickWidgets,QtQml",
            "--skip-docs",
            "--prefix=%s" % self.package_folder,
            "--parallel=%s" % tools.cpu_count(),
            "--openssl=\"%s\"" % os.path.join(self.deps_cpp_info["OpenSSL"].rootpath, "bin"),
            "--ignore-git",
        ]
        
        if self.settings.build_type == "Debug":
            arguments.append("--debug")

        if self.settings.os == "Windows":
            arguments.append("--jom")
        
        setup = os.path.join(self.source_folder, self._source_subfolder, "setup.py")
        with tools.environment_append(environment):
            with tools.chdir(self._source_subfolder): 
                if self.settings.os == "Windows":
                    python_exe = "python_d.exe" if self.settings.build_type == "Debug" else "python.exe"
                else:
                    python_exe = "python"
                self.run(python_exe + " %s install %s" % (setup, " ".join(arguments)))

    def package(self):
        """Assemble the package."""
        self.copy(pattern="LICENSE.LGPLv3", dst="licenses", src=os.path.join(self.source_folder, self._source_subfolder))

    def package_info(self):
        """Edit package info."""
        if self.settings.os == "Windows":
            self.env_info.PATH.append(os.path.join(self.package_folder, "Scripts"))
            self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "Lib", "site-packages"))
        else:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
            self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
        