import hashlib
import hmac
import re
import subprocess
from platform import uname
from sys import platform

try:
    import winreg
except ImportError:
    pass


class MachineIdNotFound(RuntimeError):
    """
    Raised when this library is unable to determine the machine id for the
    system where it is running.
    """


def __sanitize__(id: str) -> str:
    return re.sub(r"[\x00-\x1f\x7f-\x9f\s]", "", id).strip()


def __exec__(cmd: str) -> str:
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, check=True, encoding="utf-8"
        ).stdout.strip()
    except subprocess.SubprocessError:
        return None


def __read__(path: str) -> str:
    try:
        with open(path) as f:
            return f.read().strip()
    except IOError:
        return None


def __reg__() -> str:
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ,
        ) as key:
            value, regtype = winreg.QueryValueEx(key, "MachineGuid")
            return value.strip()
    except OSError:
        return None


def id() -> str:
    """
    id returns the platform specific device GUID of the current host OS.
    """

    id = None
    if platform == "darwin":
        id = __exec__(
            "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'"
        )
    elif platform in ("win32", "cygwin", "msys"):
        id = __reg__()
        if not id:
            id = __exec__(
                "powershell.exe -ExecutionPolicy bypass -command (Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"
            )
        if not id:
            id = __exec__("wmic csproduct get uuid").split("\n")[2].strip()
    elif platform.startswith("linux"):
        id = __read__("/var/lib/dbus/machine-id")
        if not id:
            id = __read__("/etc/machine-id")
        if not id:
            cgroup = __read__("/proc/self/cgroup")
            if cgroup and "docker" in cgroup:
                id = __exec__("head -1 /proc/self/cgroup | cut -d/ -f3")
        if not id:
            mountinfo = __read__("/proc/self/mountinfo")
            if mountinfo and "docker" in mountinfo:
                id = __exec__(
                    "grep -oP '(?<=docker/containers/)([a-f0-9]+)(?=/hostname)' /proc/self/mountinfo"
                )
        if not id and "microsoft" in uname().release:  # wsl
            id = __exec__(
                "powershell.exe -ExecutionPolicy bypass -command '(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID'"
            )
    elif platform.startswith(("openbsd", "freebsd")):
        id = __read__("/etc/hostid")
        if not id:
            id = __exec__("kenv -q smbios.system.uuid")

    if not id:
        raise MachineIdNotFound("failed to obtain id on platform {}".format(platform))

    return __sanitize__(id)


def hashed_id(app_id: str = "", **kwargs) -> str:
    """
    hashed_id returns the device's native GUID, hashed using HMAC-SHA256 with
    an optional application ID.
    """

    return hmac.new(
        bytes(app_id.encode()), id(**kwargs).encode(), hashlib.sha256
    ).hexdigest()
