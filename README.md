# LLMS Council

## Overview
LLMS Council is a Python-based application designed to facilitate discussions and decision-making processes among agents. It uses a pipeline of agents to process tasks and generate outputs collaboratively.

## Motivation
This project is a **fun experiment** to explore multi-agent systems and LLMs.  
It was a way to:  
- Learn about building pipelines for agent interactions.  
- Experiment with asynchronous programming in Python.  
- Improve Python skills.  
- Understand how LLMs can collaborate, debate, and make decisions in a structured workflow.  

In short, it’s both a learning playground and a showcase for agent-based reasoning with language models.

## Features
- Configurable agents with unique roles and settings.
- Pipeline execution for task processing.
- Integration with Ollama for language model interactions.
- Robust error handling and logging.

## Prerequisites
Before running the application, ensure the following dependencies are installed:

1. **Python**: Version 3.8 or higher.
2. **Ollama**: A local language model server.
3. **Required Python packages**: Listed in `requirements.txt`.

## Installation

### Step 1: Clone the Repository
```bash
# Clone the repository to your local machine
git clone https://github.com/CH-Niels/llms-council.git
cd llms-council
```

### Step 2: Install Python Dependencies
```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Install and Start Ollama
1. Download and install Ollama from the [official website](https://ollama.ai).
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Ensure Ollama is running by visiting `http://localhost:11434/v1/models`.

### Step 4: Configure Agents
1. Edit the `configs/agents_config.yaml` file to define your agents and pipeline.
2. Ensure all required models are installed in Ollama.

## Usage

### Running the Application
To start the application, run the following command:
```bash
python scripts/main.py
```

### Entering Tasks
When prompted, enter the task for the agents to process. The application will:
1. Validate the configuration.
2. Run the pipeline of agents.
3. Save the discussion log to the `logs/` directory.

## Directory Structure
- `configs/`: Contains configuration files for agents.
- `logs/`: Stores discussion logs.
- `scripts/`: Contains the main application logic.

## Troubleshooting

### Common Issues
1. **Missing Models**: Check the `configs/agents_config.yaml` file and ensure all models are installed in Ollama.

### Logs
Check the `logs/` directory for detailed logs of discussions.

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests to improve the project.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

### Python Requirements
The following Python packages are required and listed in `requirements.txt`:

- `pyyaml`: For YAML parsing.
- `requests`: For HTTP requests.
- `logging`: For logging and debugging.
- `asyncio`: For asynchronous programming.
- `ollama-sdk`: For Ollama integration.
