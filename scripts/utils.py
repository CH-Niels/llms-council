import os
import logging
from datetime import datetime

# Ensure logging is configured at the top of the file
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def collect_results(messages):
    return "\n\n".join(
        f"Source: {msg.source}\nContent: {msg.content}"
        for msg in messages
    )

def save_full_discussion(task, group_outputs, elapsed_time, folder="logs"):
    
    os.makedirs(folder, exist_ok=True)

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.txt")
    path = os.path.join(folder, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"=== Task ===\n\n{task}\n\n")

            # Save outputs for each group dynamically
            for group_name, output in group_outputs.items():
                f.write(f"=== {group_name.upper()} ===\n\n{output}\n\n")

            f.write(f"=== Elapsed Time ===\n\n{elapsed_time:.2f} seconds\n")

        print(f"\n✅ Full discussion log saved to {path}")

    except Exception as e:
        logging.error(f"Error saving discussion log: {e}")