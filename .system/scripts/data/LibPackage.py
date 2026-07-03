
import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.Utils import Utils
from scripts.db_base import Base, get_session

class LibPackage:
    class Dependency:
        def __init__(self, name:str, version:str):
            self.fullName = name
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)
            
        def matchLib(self, libPackage):
            if "/" in self.fullName:
                return self.fullName == (libPackage.publisher + "/" + libPackage.name)  \
                        and self.versionSpec.contains(Version(libPackage.version))
            
            return self.fullName == libPackage.name     \
                    and self.versionSpec.contains(Version(libPackage.version))  \
                    and libPackage.isGlobal
                    
    def __init__(self):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.mode : str = "sources"
        self.path : str = ""
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True    

    def __init__(self, path:str):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.mode : str = "sources"
        self.path : str = path
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True

        try:
            self.loadPackage()
        except:
            self.success = False

        if self.success:
            self.checkPackage()

    def __str__(self):
        return f"{self.fullName}@{self.version}"
    
    def loadPackage(self):
        path= os.path.join(self.path, "package.json")
        if not os.path.exists(path):
            self.success = False
            return
        
        self.json = Utils.loadJson(path)
        
        self.publisher = self.json.get("publisher", "")
        self.name = self.json.get("name")
        self.isGlobal = self.json.get("isGlobal", True)
        
        self.version = self.json.get("version")
        self.summary = self.json.get("summary")
        self.autoScan = False  # deprecated, always False
        dependencies = self.json.get("dependencies", {})
        for key, value in dependencies.items():
            dep = LibPackage.Dependency(key, value)
            self.dependencies.append(dep)
    
    def checkPackage(self):
        if not self.isGlobal and self.publisher == "":
            self.success = False
            assert False, f"Invalid package.json, package {self.name} is not global and publisher is missing. Path:{self.path}"
            
        assert self.name and self.version, f"Invalid package.json, package name or version is missing. Path:{self.path}"

    def isMatch(self, appPackage:AppPackage):
        if "/" in appPackage.name:
            return self.publisher == appPackage.name.split("/")[0]  \
                    and self.name == appPackage.name.split("/")[1]  \
                    and appPackage.versionSpec.contains(self.version)
         
        return self.isGlobal and self.name == appPackage.name and appPackage.versionSpec.contains(self.version)

    @classmethod
    def from_db_row(cls, row):
        """Create a LibPackage instance from a LibPackageTable ORM row."""
        lp = cls.__new__(cls)
        lp.name = row.name
        lp.publisher = row.publisher
        lp.isGlobal = row.is_global
        lp.version = row.version
        lp.summary = row.summary or ""
        lp.autoScan = False  # deprecated — always False
        lp.path = row.path
        lp.mode = row.mode or "sources"
        lp.dependencies = [
            LibPackage.Dependency(d.get("name", ""), d.get("version", ""))
            for d in (row.dependencies or [])
        ]
        lp.success = True
        return lp

    @classmethod
    def query_all_from_db(cls):
        """Query all LibPackageTable rows and return as list of LibPackage instances."""
        session = get_session()
        try:
            rows = session.query(LibPackageTable).all()
            return [cls.from_db_row(row) for row in rows]
        finally:
            session.close()


# ============================================================
# SQLAlchemy ORM models — defined under .data/ as per convention
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, UniqueConstraint


class LibPackageTable(Base):
    """ORM model mirroring LibPackage fields, stored in package.db"""
    __tablename__ = "lib_package"
    __table_args__ = (
        UniqueConstraint("publisher", "name", "version", name="uq_lib_package"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    publisher = Column(String(200), default="")
    name = Column(String(200), nullable=False)
    is_global = Column(Boolean, default=True)
    version = Column(String(50), nullable=False)
    summary = Column(Text, default="")
    mode = Column(String(50), default="sources")
    path = Column(String(1000), default="")
    dependencies = Column(JSON, default=[])

    def __repr__(self):
        return f"<LibPackageTable {self.publisher}/{self.name}@{self.version}>"


class LibPackageDetailTable(Base):
    """Per-package file scan results — one row per library.
    File paths are stored as semicolon-separated strings,
    convertible to/from Python lists via helper methods.
    """
    __tablename__ = "lib_package_detail"
    __table_args__ = (
        UniqueConstraint("group", "name", "version", name="uq_lib_package_detail"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(1000), default="")
    name = Column(String(200), nullable=False)
    group = Column(String(200), default="")
    version = Column(String(50), nullable=False)
    headers = Column(Text, default="")
    sources = Column(Text, default="")
    uis = Column(Text, default="")
    resources = Column(Text, default="")
    definitions = Column(Text, default="")
    includes = Column(Text, default="")
    precompile_headers = Column(Text, default="")
    dynamic_definition = Column(Text, default="")

    # Semicolon separator for file lists
    SEP = ";"

    def __repr__(self):
        return f"<LibPackageDetailTable {self.group}/{self.name}@{self.version}>"

    @classmethod
    def list_to_str(cls, file_list):
        """Convert a list of strings to semicolon-separated string."""
        if not file_list:
            return ""
        return cls.SEP.join(file_list)

    @classmethod
    def str_to_list(cls, file_str):
        """Convert a semicolon-separated string back to list of strings."""
        if not file_str or not file_str.strip():
            return []
        return [f for f in file_str.split(cls.SEP) if f.strip()]

    def get_headers(self):
        return self.str_to_list(self.headers)

    def get_sources(self):
        return self.str_to_list(self.sources)

    def get_uis(self):
        return self.str_to_list(self.uis)

    def get_resources(self):
        return self.str_to_list(self.resources)

    def get_definitions(self):
        return self.str_to_list(self.definitions)

    def get_includes(self):
        return self.str_to_list(self.includes)

    def get_precompile_headers(self):
        return self.str_to_list(self.precompile_headers)

    def get_dynamic_definition(self):
        return self.str_to_list(self.dynamic_definition)