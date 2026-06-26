import pandas as pd
import os

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
        except Exception as e:
            print(f"❌ Error converting {json_path}: {e}")

    print("All files processed!")


# Define your file paths as discrete variables here
ollama_json_output = r"C:\Users\User\Desktop\md_tool\final_data_ollama.json"
staged_bls_output = r"C:\Users\User\Desktop\md_tool\staged_bls.json"
staged_containers_output = r"C:\Users\User\Desktop\md_tool\staged_containers.json"

# Define the target export directory
export_folder = r"C:\Users\User\Desktop\md_tool\Export_Tools"

# Pass one or many variables into the list
files_to_convert = [
    ollama_json_output,
    staged_bls_output,
    staged_containers_output
]

# Call the reusable function directly
convert_json_to_excel(files_to_convert, export_folder)