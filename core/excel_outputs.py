import pandas as pd
import os
from pathlib import Path

def convert_json_to_excel(json_file_paths: list[str], output_dir: str):
    """
    Takes a list of JSON file paths, converts each to a Pandas DataFrame,
    and exports them to Excel files in the specified output directory.
    """
    print("Starting conversion...")
    
    # Ensure the target export directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for json_path in json_file_paths:
        # Extract just the filename (e.g., 'final_data_ollama.json') from the full path
        filename = os.path.basename(json_path)
        
        # Swap the extension and glue it to the new output directory
        excel_filename = filename.replace('.json', '.xlsx')
        excel_path = os.path.join(output_dir, excel_filename)
        
        try:
            # The optimized Pandas approach:
            df = pd.read_json(json_path)
            df.to_excel(excel_path, index=False)
            
            print(f"✅ Saved: {excel_path}")
        except FileNotFoundError:
            print(f"⚠️ Skipped: {filename} (File not found. Did you run the pipeline yet?)")
        except ValueError:
            print(f"⚠️ Skipped: {filename} (JSON file is empty or invalid)")
        except Exception as e:
            print(f"❌ Error converting {json_path}: {e}")

    print("All files processed!")

if __name__ == "__main__":
    # Resolve the root directory of the repository (1 level up from core/excel_outputs.py)
    root_dir = Path(__file__).resolve().parent.parent
    
    # Target the new organized outputs folders
    json_dir = root_dir / "data" / "outputs" / "json"
    excel_dir = root_dir / "data" / "outputs" / "excel"
    
    # Define your file paths based on the new folder structure
    ollama_json_output = json_dir / "final_data_ollama.json"
    staged_bls_output = json_dir / "staged_bls.json"
    staged_containers_output = json_dir / "staged_containers.json"
    
    # Pass one or many variables into the list (converting Path objects to strings)
    files_to_convert = [
        str(ollama_json_output),
        str(staged_bls_output),
        str(staged_containers_output)
    ]
    
    # Call the reusable function directly, exporting the Excels into the excel folder
    convert_json_to_excel(files_to_convert, str(excel_dir))