import subprocess
import requests
import time
import sys

def check_ollama():
    try:
        resp = requests.get("http://localhost:11434/v1/models")
        if resp.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print(f"⚠ Unexpected response: {resp.status_code}")
    except requests.ConnectionError:
        return False
    return False

def start_ollama():
    """Start Ollama using `ollama serve` in the background and wait until ready."""
    print("🚀 Starting Ollama with `ollama serve`...")
    # Start Ollama in the background
    subprocess.Popen(["ollama", "serve"], stdout=sys.stdout, stderr=sys.stderr)
    # Wait a few seconds for Ollama to be ready
    for i in range(15):
        time.sleep(1)
        if check_ollama():
            print("✅ Ollama is now running")
            return True
    print("❌ Failed to start Ollama")
    return False

def ensure_ollama():
    if not check_ollama():
        if not start_ollama():
            sys.exit(1)
    print("All good — you can now start your agents!")