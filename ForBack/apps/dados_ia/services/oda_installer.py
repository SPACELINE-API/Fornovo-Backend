import os
import subprocess
import urllib.request
import urllib.error
import winreg
import sys
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import ttk

ODA_VERSION = "27.1"
ODA_URL = f"https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_vc16_amd64dll_{ODA_VERSION}.msi"
ODA_INSTALL_PATH = Path(f"C:/Program Files/ODA/ODAFileConverter {ODA_VERSION}.0")
ODA_EXE = ODA_INSTALL_PATH / "ODAFileConverter.exe"
INSTALLER_PATH = Path("C:/Temp/ODAFileConverter_installer.msi")
LOG_PATH = Path("C:/Temp/oda_install.log")
FLAG_FILE = Path("C:/Temp/oda_installed.flag")


def is_oda_ready() -> bool:
    return ODA_EXE.exists()


def is_valid_msi(path: Path) -> bool:
    try:
        if path.stat().st_size < 1024:
            return False
        with open(path, "rb") as f:
            return f.read(4) == b"\xd0\xcf\x11\xe0"
    except Exception:
        return False


class DownloadScreen:
    def __init__(self, title="Baixando ODA File Converter"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("420x150")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.label = tk.Label(self.root, text="Preparando download...", font=("Segoe UI", 11))
        self.label.pack(pady=(20, 10))

        self.progress = ttk.Progressbar(self.root, length=360, mode="determinate", maximum=100)
        self.progress.pack(pady=5)

        self.percent_label = tk.Label(self.root, text="0%", font=("Segoe UI", 10, "bold"))
        self.percent_label.pack(pady=(2, 10))

        self.root.update()

    def update(self, pct: float, downloaded_mb: float, total_mb: float):
        self.progress["value"] = pct
        self.percent_label.config(text=f"{pct:.1f}%  ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)")
        self.label.config(text="Baixando ODA File Converter...")
        self.root.update_idletasks()
        self.root.update()

    def update_indeterminate(self, downloaded_mb: float):
        self.label.config(text="Baixando ODA File Converter...")
        self.percent_label.config(text=f"{downloaded_mb:.1f} MB baixados...")
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()


def download_installer(max_retries: int = 3) -> bool:
    INSTALLER_PATH.parent.mkdir(parents=True, exist_ok=True)

    screen = DownloadScreen()

    for attempt in range(1, max_retries + 1):
        if INSTALLER_PATH.exists():
            INSTALLER_PATH.unlink()

        try:
            screen.label.config(text=f"Baixando ODA... (tentativa {attempt}/{max_retries})")

            req = urllib.request.Request(ODA_URL, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/octet-stream,*/*",
                "Referer": "https://www.opendesign.com/guestfiles",
            })

            with urllib.request.urlopen(req, timeout=120) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(INSTALLER_PATH, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size:
                            pct = downloaded / total_size * 100
                            baixado_mb = downloaded / 1024 / 1024
                            total_mb = total_size / 1024 / 1024
                            screen.update(pct, baixado_mb, total_mb)
                        else:
                            screen.update_indeterminate(downloaded / 1024 / 1024)

            if is_valid_msi(INSTALLER_PATH):
                screen.close()
                return True

        except Exception:
            continue

    screen.close()
    return False


def install_oda() -> bool:
    if not INSTALLER_PATH.exists() or not is_valid_msi(INSTALLER_PATH):
        return False

    result = subprocess.run(
        ["msiexec", "/i", str(INSTALLER_PATH), "/quiet", "/norestart", "/l*v", str(LOG_PATH)],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def add_to_path():
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
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, current_path.rstrip(";") + ";" + oda_path)

    winreg.CloseKey(key)

    broadcast = ctypes.c_long()
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(broadcast)
    )

    os.environ["PATH"] = os.environ.get("PATH", "") + ";" + oda_path


def install_as_admin() -> bool:
    script = Path(__file__).resolve()
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}"', None, 1
    )
    return ret > 32


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        sys.exit(1)

    if not ODA_EXE.exists():
        if not download_installer():
            sys.exit(1)

        if not install_oda():
            sys.exit(1)

        if INSTALLER_PATH.exists():
            INSTALLER_PATH.unlink()

    add_to_path()

    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.touch()