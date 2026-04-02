import os
import subprocess
import urllib.request
import winreg
import sys
import ctypes
from pathlib import Path

ODA_VERSION = "27.1"
ODA_URL = f"https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_vc16_amd64dll_{ODA_VERSION}.msi"
ODA_INSTALL_PATH = Path(f"C:/Program Files/ODA/ODAFileConverter {ODA_VERSION}.0")
ODA_EXE = ODA_INSTALL_PATH / "ODAFileConverter.exe"
INSTALLER_PATH = Path("C:/Temp/ODAFileConverter_installer.msi")
LOG_PATH = Path("C:/Temp/oda_install.log")


def ensure_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Solicitando privilégios de administrador...")
        script = Path(__file__).resolve()
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}"', None, 1
        )
        sys.exit(0)


def ensure_oda_installed() -> bool:
    if ODA_EXE.exists():
        print("ODA já está instalado.")
        return True

    ensure_admin()

    print("ODA não encontrado, iniciando instalação.")

    try:
        INSTALLER_PATH.parent.mkdir(parents=True, exist_ok=True)

        print("Baixando instalador...")
        with urllib.request.urlopen(ODA_URL) as response, open(INSTALLER_PATH, "wb") as f:
            total = response.length or 0
            downloaded = 0
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\rDownload: {pct:.1f}% ({downloaded//1024//1024} MB)", end="")
        print("\nDownload concluído.")

        print("Instalando ODA...")
        result = subprocess.run(
            ["msiexec", "/i", str(INSTALLER_PATH), "/quiet", "/norestart", "/l*v", str(LOG_PATH)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Erro na instalação.")
            print(result.stderr)
            return False

        print("Instalação concluída.")

        oda_path = str(ODA_INSTALL_PATH)
        print("Atualizando PATH...")

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

        if oda_path not in current_path:
            winreg.SetValueEx(
                key,
                "Path",
                0,
                winreg.REG_EXPAND_SZ,
                current_path.rstrip(";") + ";" + oda_path
            )

        winreg.CloseKey(key)

        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.c_long()
        )

        print("PATH atualizado.")

        return ODA_EXE.exists()

    except Exception as e:
        print(f"Erro geral: {e}")
        return False


if __name__ == "__main__":
    ok = ensure_oda_installed()
    if ok:
        print("ODA pronto para uso")
    else:
        print("Falha ao instalar ODA")