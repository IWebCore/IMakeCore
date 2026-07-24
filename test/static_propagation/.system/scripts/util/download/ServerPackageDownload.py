from scripts.util.download.BaseDownloader import BaseDownloader


class ServerPackageDownload(BaseDownloader):
    def download(self):
        # TODO: implement server-based package download
        # GET /package/download?name={name}&version={version}
        raise NotImplementedError("ServerPackageDownload not yet implemented")

    def validate(self):
        return False
