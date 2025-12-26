import json
import os
from dotenv import load_dotenv
from orchestrator import run_pipeline

INPUT_FILE = "inputs/glowboost_input.json"
OUTPUT_FILE = "output.json"

def main():
    load_dotenv()
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        return

    try:
        with open(INPUT_FILE, "r") as f:
            raw_input = json.load(f)
        
        print(f"Loaded input from {INPUT_FILE}")
        
        result = run_pipeline(raw_input)
        
        # Use the new save_outputs function
        from orchestrator import save_outputs
        save_outputs(result, output_dir="outputs")
            
        print(f"Pipeline executed successfully. Outputs saved to 'outputs/' directory.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
