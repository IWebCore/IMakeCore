import os
import time
import zipfile
import requests
from scripts.util.download.BaseDownloader import BaseDownloader


class UrlPackageDownload(BaseDownloader):
    def download(self):
        cache = os.path.join(self.env.sysCachePath,
                             f"{self.ref.name}_{int(time.time())}.zip")
        try:
            for url in (self.ref.url or []):
                if self._fetch(url, cache):
                    return self._unpack(cache)
            return False
        finally:
            if os.path.exists(cache):
                os.remove(cache)

    def _fetch(self, url, dest):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(r.content)
                return True
        except Exception:
            pass
        return False

    def _unpack(self, zip_path):
        os.makedirs(self.target_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(self.target_dir)
        return True

    def validate(self):
        return (os.path.exists(os.path.join(self.target_dir, "package.json"))
                or self.ref.resolve is not None)
