import os
from scripts.data import *
from packaging import version
import requests

class LocatePackages:
    def __init__(self, package : AppPackage, env : EnvConfig):
        self.package = package
        self.env = env
        self.success = False
        self.matchPackage()

    def matchPackage(self):
        if self.package.path is not None and self.package.path.strip() != '':
            lib = LibPackage(self.package.path)
            if lib.isMatch(self.package):
                self.package.libPackage = lib
                self.success = True
                return
            else:
                print(f"Package {self.package.group}/{self.package.name} not found in user defined path: { self.package.path}")
                exit(1)

        lib : LibPackage
        for lib  in self.env.libs:
            if lib.isMatch(self.package):
                self.package.libPackage = lib
                self.success = True
                return
                    