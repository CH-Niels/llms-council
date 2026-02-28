import subprocess
import requests
import time
import sys
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ollama():
    print("🔍 Checking if Ollama is running...")
    try:
        resp = requests.get("http://localhost:11434/v1/models")
        if resp.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            logging.error(f"Unexpected status code from Ollama: {resp.status_code}")
            return False
    except requests.ConnectionError as e:
        logging.error(f"Connection error while checking Ollama: {e}")
        return False

def start_ollama():
    print("🚀 Attempting to start Ollama with `ollama serve`...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=sys.stdout, stderr=sys.stderr)
    except FileNotFoundError:
        logging.error("`ollama` command not found. Ensure it is installed and in PATH.")
        return False
    except Exception as e:
        logging.error(f"Failed to start Ollama: {e}")
        return False

    # Wait a few seconds for Ollama to be ready
    for i in range(15):
        print(f"⏳ Waiting for Ollama to start... ({i + 1}/15)")
        time.sleep(1)
        if check_ollama():
            print("✅ Ollama is now running")
            return True
    logging.error("Failed to start Ollama after multiple attempts.")
    return False

def check_models_installed(config_path="configs/agents_config.yaml"):
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
            except requests.ConnectionError as e:
                logging.error(f"Unable to connect to Ollama while checking model {model}: {e}")
                return False

        if missing_models:
            logging.error(f"Missing models: {', '.join(missing_models)}")
            return False

        print("✅ All models are installed.")
        return True

    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return False
    except KeyError as e:
        logging.error(f"Invalid configuration format. Missing key: {e}")
        return False
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML configuration: {e}")
        return False

def ensure_ollama():
    if not check_ollama():
        if not start_ollama():
            sys.exit(1)
    if not check_models_installed():
        sys.exit(1)
