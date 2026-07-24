import os
import subprocess
from scripts.util.download.BaseDownloader import BaseDownloader


class GitPackageDownload(BaseDownloader):
    def download(self):
        url = self.ref.git.url
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, self.target_dir],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"ERROR: git clone failed: {result.stderr.strip()}")
            return False

        checkout_ref = (self.ref.git.hash or
                        f"tags/{self.ref.git.tag}" if self.ref.git.tag else
                        self.ref.git.branch)

        if checkout_ref:
            result = subprocess.run(
                ["git", "-C", self.target_dir, "checkout", checkout_ref],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"ERROR: git checkout failed: {result.stderr.strip()}")
                return False

        return True

    def validate(self):
        return (os.path.exists(os.path.join(self.target_dir, "package.json"))
                or self.ref.resolve is not None)
