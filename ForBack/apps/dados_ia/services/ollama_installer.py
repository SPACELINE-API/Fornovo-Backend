import subprocess
import requests
import time
import urllib.request
import os

MODELOS = ["nomic-embed-text", "minimax-m2.7:cloud"]


def ollama_instalado() -> bool:
    try:
        result = subprocess.run(["ollama", "-v"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def ollama_rodando() -> bool:
    try:
        requests.get("http://127.0.0.1:11434", timeout=1)
        return True
    except:
        return False


def modelos_instalados() -> bool:
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    output = result.stdout.lower()
    return all(m.lower() in output for m in MODELOS)


def ensure_ollama_ready():
    if not ollama_instalado():
        print("Instalando Ollama")
        installer_path = os.path.join(
            os.environ.get("TEMP", "C:\\Temp"), "OllamaSetup.exe"
        )
        urllib.request.urlretrieve(
            "https://ollama.com/download/OllamaSetup.exe", installer_path
        )
        subprocess.run([installer_path, "/SILENT"], check=True)

    if not ollama_rodando():
        print("Iniciando Ollama")
        subprocess.Popen("ollama serve", shell=True)

        for _ in range(10):
            if ollama_rodando():
                break
            time.sleep(1)

    if not modelos_instalados():
        print("Baixando modelos...")
        for m in MODELOS:
            subprocess.run(["ollama", "pull", m])


def ensure_ollama_cuda() -> dict:
    gpu_info = {"cuda_active": False, "gpu_name": None, "vram_mb": None}

    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return gpu_info

        linha = result.stdout.strip().split("\n")[0]
        nome, memoria = [x.strip() for x in linha.split(",")]

        gpu_info["gpu_name"] = nome
        gpu_info["vram_mb"] = int(memoria)

        gpu_info["cuda_active"] = True

    except FileNotFoundError:
        pass
    except Exception:
        pass

    return gpu_info
