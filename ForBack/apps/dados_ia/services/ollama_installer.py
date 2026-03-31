import os
import re
import subprocess
import urllib.request
import urllib.error
import winreg
import sys
import ctypes
import json
import time
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import ttk

OLLAMA_URL = "https://ollama.com/download/OllamaSetup.exe"
INSTALLER_PATH = Path("C:/Temp/OllamaSetup.exe")
FLAG_FILE = Path("C:/Temp/ollama_installed.flag")

MODELOS = [
    "llama3.1:8b",
    "nomic-embed-text",
]

POSSIBLE_PATHS = [
    Path(os.environ.get("ProgramFiles", "")) / "Ollama" / "ollama.exe",
    Path(os.environ.get("ProgramFiles(x86)", "")) / "Ollama" / "ollama.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",
]


def is_ollama_ready() -> bool:
    if shutil.which("ollama"):
        return True

    for path in POSSIBLE_PATHS:
        if path.exists():
            return True

    try:
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]
        for reg_path in reg_paths:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    if "Ollama" in display_name:
                        return True
                except Exception:
                    pass
                finally:
                    winreg.CloseKey(subkey)
            winreg.CloseKey(key)
    except Exception:
        pass

    return False


def has_nvidia_gpu() -> bool:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_gpu_info() -> dict:
    info = {"gpu": False, "cuda": False, "gpu_name": "", "vram_mb": 0}

    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            info["gpu"] = True
            info["gpu_name"] = parts[0].strip()
            if len(parts) > 1:
                vram_str = re.search(r"(\d+)", parts[1])
                if vram_str:
                    info["vram_mb"] = int(vram_str.group(1))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return info

    cuda_indicators = [
        shutil.which("nvcc") is not None,
        os.path.exists(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"),
        bool(os.environ.get("CUDA_PATH")),
        os.path.exists(r"C:\Windows\System32\nvcuda.dll"),
    ]
    info["cuda"] = any(cuda_indicators)

    return info


def _is_ollama_running() -> bool:
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
        return True
    except Exception:
        return False


def _wait_ollama_ready(timeout: int = 30):
    for _ in range(timeout):
        if _is_ollama_running():
            return True
        time.sleep(1)
    return False


def _ollama_has_cuda() -> bool:
    try:
        r = subprocess.run(
            ["powershell", "-Command",
             "(Get-Process ollama -ErrorAction SilentlyContinue | "
             "Get-ProcessModule | Where-Object {$_.ModuleName -match 'cuda|nvcuda'}).Count"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0 and r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0
    except Exception:
        return False


def ensure_ollama_cuda() -> dict:
    gpu = get_gpu_info()

    if not gpu["gpu"] or not gpu["cuda"]:
        gpu["cuda_active"] = False
        return gpu

    cuda_bin = None
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path:
        candidate = Path(cuda_path) / "bin"
        if candidate.exists():
            cuda_bin = str(candidate)
    if cuda_bin is None:
        toolkit = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA")
        if toolkit.exists():
            versions = sorted(toolkit.iterdir(), reverse=True)
            for v in versions:
                candidate = v / "bin"
                if candidate.exists():
                    cuda_bin = str(candidate)
                    break

    if cuda_bin:
        os.environ["CUDA_HOME"] = str(Path(cuda_bin).parent)
        current_path = os.environ.get("PATH", "")
        if cuda_bin not in current_path:
            os.environ["PATH"] = cuda_bin + ";" + current_path

    ollama_exe = shutil.which("ollama") or _find_ollama_exe()
    if ollama_exe is None:
        gpu["cuda_active"] = False
        return gpu

    if _is_ollama_running() and _ollama_has_cuda():
        gpu["cuda_active"] = True
        return gpu

    env = os.environ.copy()

    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "ollama.exe"],
            capture_output=True, timeout=10,
        )
        time.sleep(2)
    except Exception:
        pass

    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        gpu["cuda_active"] = False
        return gpu

    _wait_ollama_ready(30)
    time.sleep(2)

    gpu["cuda_active"] = True
    return gpu


def _find_ollama_exe() -> str | None:
    for p in POSSIBLE_PATHS:
        if p.exists():
            return str(p)
    return None


class DownloadScreen:
    def __init__(self, title="Baixando Ollama"):
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
        self.label.config(text="Baixando Ollama...")
        self.root.update_idletasks()
        self.root.update()

    def update_indeterminate(self, downloaded_mb: float):
        self.label.config(text="Baixando Ollama...")
        self.percent_label.config(text=f"{downloaded_mb:.1f} MB baixados...")
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()


class ModelDownloadScreen:
    def __init__(self, modelo_nome: str):
        self.root = tk.Tk()
        self.root.title(f"Baixando modelo: {modelo_nome}")
        self.root.geometry("420x180")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.label = tk.Label(self.root, text=f"Baixando {modelo_nome}...", font=("Segoe UI", 11))
        self.label.pack(pady=(20, 5))

        self.status_label = tk.Label(self.root, text="Preparando...", font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 5))

        self.progress = ttk.Progressbar(self.root, length=360, mode="determinate", maximum=100)
        self.progress.pack(pady=5)

        self.percent_label = tk.Label(self.root, text="0%", font=("Segoe UI", 10, "bold"))
        self.percent_label.pack(pady=(2, 10))

        self.root.update()

    def _apply_json(self, text: str):
        text = text.strip()
        if not text:
            return
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return

        status = data.get("status", "")

        if "total" in data and "completed" in data:
            total = data["total"]
            completed = data["completed"]
            if total > 0:
                pct = completed / total * 100
                self.progress["value"] = pct
                total_mb = total / 1024 / 1024
                completed_mb = completed / 1024 / 1024
                self.percent_label.config(text=f"{pct:.1f}%  ({completed_mb:.1f} MB / {total_mb:.1f} MB)")
                self.status_label.config(text=status)
        elif status:
            self.status_label.config(text=status)

        self.root.update_idletasks()
        self.root.update()

    def update_from_chunk(self, chunk: str):
        for line in chunk.split("\r"):
            self._apply_json(line)

    def close(self):
        self.root.destroy()


def download_installer(max_retries: int = 3) -> bool:
    INSTALLER_PATH.parent.mkdir(parents=True, exist_ok=True)

    screen = DownloadScreen()

    for attempt in range(1, max_retries + 1):
        if INSTALLER_PATH.exists():
            INSTALLER_PATH.unlink()

        try:
            screen.label.config(text=f"Baixando Ollama... (tentativa {attempt}/{max_retries})")

            req = urllib.request.Request(OLLAMA_URL, headers={"User-Agent": "Mozilla/5.0"})

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

            if INSTALLER_PATH.exists() and INSTALLER_PATH.stat().st_size > 1024:
                screen.close()
                return True

        except urllib.error.URLError:
            pass
        except Exception:
            pass

    screen.close()
    return False


def install_ollama() -> bool:
    if not INSTALLER_PATH.exists():
        return False

    result = subprocess.run(
        [str(INSTALLER_PATH), "/S"],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def add_to_path():
    possible_dirs = [str(p.parent) for p in POSSIBLE_PATHS if p.exists()]
    if not possible_dirs:
        return

    ollama_path = possible_dirs[0]

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

    if ollama_path not in current_path.split(";"):
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, current_path.rstrip(";") + ";" + ollama_path)

    winreg.CloseKey(key)

    broadcast = ctypes.c_long()
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(broadcast)
    )

    os.environ["PATH"] = os.environ.get("PATH", "") + ";" + ollama_path


def modelos_instalados() -> list[str]:
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        linhas = result.stdout.strip().splitlines()
        modelos = []
        for linha in linhas[1:]:
            partes = linha.strip().split()
            if partes:
                modelos.append(partes[0])
        return modelos
    except Exception:
        return []


def _modelo_ja_instalado(modelo: str, instalados: list[str]) -> bool:
    modelo_base = modelo.split(":")[0]
    for inst in instalados:
        inst_base = inst.split(":")[0]
        if inst_base == modelo_base:
            return True
    return False


def pull_modelos():
    print("\nVerificando modelos...")
    instalados = modelos_instalados()

    for modelo in MODELOS:
        if _modelo_ja_instalado(modelo, instalados):
            print(f"  {modelo} já instalado. Pulando.")
            continue

        print(f"\n  Pulling {modelo}...")

        screen = ModelDownloadScreen(modelo)

        process = subprocess.Popen(
            ["ollama", "pull", modelo],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        while True:
            chunk = process.stderr.read1(4096) if hasattr(process.stderr, "read1") else process.stderr.read(4096)
            if chunk:
                text = chunk.decode("utf-8", errors="replace")
                screen.update_from_chunk(text)
            elif process.poll() is not None:
                break

        process.wait()
        screen.close()

        print(f"  {modelo} pronto." if process.returncode == 0 else f"  Falha ao baixar {modelo}.")


def _instalar_como_admin():
    script = Path(__file__).resolve()
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}"', None, 1
    )


def _rotina_instalacao():
    print("=" * 50)
    print("Instalador automático do Ollama")
    print("=" * 50)

    if not download_installer():
        input("\nFalha no download. Pressione Enter para fechar...")
        sys.exit(1)

    print("Instalando Ollama...")
    if not install_ollama():
        input("\nFalha na instalação. Pressione Enter para fechar...")
        sys.exit(1)

    if INSTALLER_PATH.exists():
        INSTALLER_PATH.unlink()

    print("Ollama instalado com sucesso!")

    add_to_path()

    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.touch()

    pull_modelos()

    print("\nOllama pronto para uso.")
    input("\nPressione Enter para fechar...")


def ensure_ollama_ready():
    if is_ollama_ready():
        pull_modelos()
        return

    if not ctypes.windll.shell32.IsUserAnAdmin():
        _instalar_como_admin()
        return

    _rotina_instalacao()


if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        _rotina_instalacao()
    else:
        ensure_ollama_ready()
