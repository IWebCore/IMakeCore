import json
import os
import time
import zipfile
from packaging.version import Version
from scripts.data import *
import requests

class DownloadPackage:
    def __init__(self, package:AppPackage, env:EnvConfig):
        self.package = package
        self.env = env
        self.success = False
        
        self.cachePath = os.path.join(env.sysCachePath, f"{self.package.name}_{str(time.time())}.zip")
        self.libPath = ""
        
        self.process()
        os.remove(self.cachePath)

    def process(self):
        if self.download() and self.uppackPackage() and self.matchPackage():
            self.package.path = self.libPath
            self.package.libPackage = LibPackage(self.libPath)
            self.success = True

    def download(self):
        if self.package.urls is not None and len(self.package.urls) > 0:
            if not self.downloadByUrl(self.package.urls):
                print(f"Failed to download {self.package.name} from given urls: {self.package.urls}")
                exit(1)
            return True
                    
        if not self.downloadByServer():
            print(f"Failed to download {self.package.name} version {self.package.version} from server")
            exit(1)
            
        return True

    def uppackPackage(self):
        json = self.readPackageJson()
        if json is None:
            print(f"Failed to read package.json from downloaded package: {self.package.name}")
            exit(1)

        if not self.checkDownloadedPackage(json):
            print(f"Downloaded package is not the same as required")
            exit(1)
        
        self.libPath = os.path.join(self.env.sysLibStore, f"{self.package.name}@{json.get('version' )}")
        if not os.path.exists(self.libPath):
            os.makedirs(self.libPath, exist_ok=False)
        
        with zipfile.ZipFile(self.cachePath, 'r') as zip_ref:
            zip_ref.extractall(self.libPath)

        return True
        
    def matchPackage(self):
        lib = LibPackage(self.libPath)
        if not lib.success:
            print(f"Failed to load library package: {self.package.name}")
            exit(1)
        if(lib.isMatch(self.package)):
            self.package.libPackage = lib
            return True
        else:
            print(f"Library package {self.package.name} is not match with app package")
            exit(1)

    def getPotensialUrls(self):
        urls = []
        for path in self.env.servers:
            url = os.path.join(path, self.package.name+".zip")
            urls.append(url)
        return urls
    
    def downloadByUrl(self, urls: list[str]):
        for url in urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(self.cachePath, "wb") as f:
                        f.write(response.content)
                    self.success = True
                    print(f'download {self.package.name} from {url} success')
                    return True
            except:
                pass
            
        return False
        
    def downloadByServer(self):
    
        for server in self.env.servers:
            url = os.path.join(server, "package", "download", self.package.name, self.package.version).replace(os.sep, "/")
            if self.package.version == "*" or self.package.version == "latest":
                url = os.path.join(server, "package", "download", self.package.name, "latest").replace(os.sep, "/")
            
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(self.cachePath, "wb") as f:
                        f.write(response.content)
                        
                    print(f'download {self.package.name} from {server} success')
                    self.success = True
                    return True
            except:
                pass
            
        return False
    
    def readPackageJson(self):
        with zipfile.ZipFile(self.cachePath, 'r') as zip_ref:
        # 检查是否存在package.json
            if 'package.json' in zip_ref.namelist():
                # 读取文件内容
                with zip_ref.open('package.json') as json_file:
                    data = json.load(json_file)
                    return data
            else:
                return None
            

    def checkDownloadedPackage(self, val):
        if val.get("name", "") != self.package.name:
            return False
        
        if self.package.version == "*" or self.package.version == "latest":
            return True
        
        return self.package.versionSpec.contains(Version(val.get("version")))