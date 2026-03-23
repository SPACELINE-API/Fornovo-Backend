import os
import subprocess
import urllib.request
import winreg
import sys
import ctypes
from pathlib import Path

ODA_VERSION = "27.1"
ODA_URL = f"https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_vc16_amd64dll_{ODA_VERSION}.msi"
ODA_INSTALL_PATH = Path("C:/Program Files/ODA/ODAFileConverter")
INSTALLER_PATH = Path("C:/Temp/ODAFileConverter_installer.msi")
LOG_PATH = Path("C:/Temp/oda_install.log")
FLAG_FILE = Path("C:/Temp/oda_installed.flag")


def ensure_oda_ready():
    try:
        oda_exe = ODA_INSTALL_PATH / "ODAFileConverter.exe"

        if oda_exe.exists() and FLAG_FILE.exists():
            return {
                "ok": True,
                "oda_path": str(oda_exe)
            }

        if not ctypes.windll.shell32.IsUserAnAdmin():
            script = Path(__file__).resolve()
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}"', None, 1
            )
            if ret <= 32:
                return {"ok": False, "error": "Falha ao obter privilégios de admin"}
            sys.exit(0)

        if not oda_exe.exists():
            INSTALLER_PATH.parent.mkdir(parents=True, exist_ok=True)

            def is_valid_msi(path: Path):
                try:
                    if path.stat().st_size < 1024:
                        return False
                    with open(path, "rb") as f:
                        return f.read(4) == b"\xd0\xcf\x11\xe0"
                except:
                    return False

            for _ in range(3):
                if INSTALLER_PATH.exists():
                    INSTALLER_PATH.unlink()

                try:
                    req = urllib.request.Request(ODA_URL, headers={
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/octet-stream,*/*",
                        "Referer": "https://www.opendesign.com/guestfiles",
                    })

                    with urllib.request.urlopen(req, timeout=120) as r:
                        with open(INSTALLER_PATH, "wb") as f:
                            while True:
                                chunk = r.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)

                    if is_valid_msi(INSTALLER_PATH):
                        break
                except:
                    continue
            else:
                return {"ok": False, "error": "Falha no download do ODA"}

            result = subprocess.run(
                ["msiexec", "/i", str(INSTALLER_PATH), "/quiet", "/norestart", "/l*v", str(LOG_PATH)],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {"ok": False, "error": f"Erro na instalação: {result.returncode}"}

            if INSTALLER_PATH.exists():
                INSTALLER_PATH.unlink()

        oda_path = str(ODA_INSTALL_PATH)

        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            )
        except PermissionError:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            )

        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path = ""

        if oda_path not in current_path.split(";"):
            winreg.SetValueEx(
                key,
                "Path",
                0,
                winreg.REG_EXPAND_SZ,
                current_path.rstrip(";") + ";" + oda_path
            )

        winreg.CloseKey(key)

        os.environ["PATH"] = os.environ.get("PATH", "") + ";" + oda_path

        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(result)
        )

        if not oda_exe.exists():
            return {"ok": False, "error": "Executável não encontrado após instalação"}

        FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
        FLAG_FILE.touch()

        return {
            "ok": True,
            "oda_path": str(oda_exe)
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}