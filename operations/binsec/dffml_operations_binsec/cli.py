from dffml import CMD

from .distro.clearlinux import ClearLinux


class ClearLinuxCMD(CMD):
    async def run(self):
        return await ClearLinux().report()


class DistroCMD(CMD):
    clearlinux = ClearLinuxCMD


class ScanCMD(CMD):
    distro = DistroCMD


class BinSecCMD(CMD):
    scan = ScanCMD
