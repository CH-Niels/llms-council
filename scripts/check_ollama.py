import subprocess
import requests
import time
import sys
import yaml

def check_ollama():
    print("🔍 Checking if Ollama is running...")
    try:
        resp = requests.get("http://localhost:11434/v1/models")
        if resp.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            return False
    except requests.ConnectionError:
        return False

def start_ollama():
    """Start Ollama using `ollama serve` in the background and wait until ready."""
    print("🚀 Attempting to start Ollama with `ollama serve`...")
    # Start Ollama in the background
    subprocess.Popen(["ollama", "serve"], stdout=sys.stdout, stderr=sys.stderr)
    # Wait a few seconds for Ollama to be ready
    for i in range(15):
        print(f"⏳ Waiting for Ollama to start... ({i + 1}/15)")
        time.sleep(1)
        if check_ollama():
            print("✅ Ollama is now running")
            return True
    print("❌ Failed to start Ollama after multiple attempts.")
    return False

def check_models_installed(config_path="configs/agents_config.yaml"):
    """Check if all required models are installed based on the agents_config.yaml file."""
    print("🔍 Checking if all required models are installed...")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        agent_configs = config.get("agents", {})
        model_names = [agent["llm_config"]["model"] for agent in agent_configs.values()]

        missing_models = []
        for model in model_names:
            try:
                resp = requests.get(f"http://localhost:11434/v1/models/{model}")
                if resp.status_code != 200:
                    missing_models.append(model)
            except requests.ConnectionError:
                print("❌ Unable to connect to Ollama. Ensure it is running.")
                return False

        if missing_models:
            print("❌ Missing models:", ", ".join(missing_models))
            return False

        print("✅ All models are installed.")
        return True

    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False
    except KeyError as e:
        print(f"❌ Invalid configuration format. Missing key: {e}")
        return False

def ensure_ollama():
    if not check_models_installed():
        sys.exit(1)
    if not check_ollama():
        if not start_ollama():
            sys.exit(1)
