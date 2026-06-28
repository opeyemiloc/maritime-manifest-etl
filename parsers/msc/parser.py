import json
import os
from pathlib import Path

# Use absolute imports based on the new folder structure
from parsers.msc import pipeline
from core import ai_pipeline
from utils.run_md import convert_pdf_to_md
from core.excel_outputs import convert_json_to_excel  # <-- 1. Import your Excel converter

def run_staging_phase(excel_filepath, md_filepath, bl_out_json, cn_out_json):
    print("\n" + "="*45)
    print(" PHASE 1: DATA STAGING & NORMALIZATION")
    print("="*45)
    
    # We pass the file paths as strings to ensure compatibility with other scripts
    normalized_data = pipeline.process_manifest(str(excel_filepath), str(md_filepath))
    
    # Ensure the target json output directories exist before writing
    os.makedirs(os.path.dirname(bl_out_json), exist_ok=True)
    
    with open(bl_out_json, 'w', encoding='utf-8') as out_f:
        json.dump(normalized_data["bl_data"], out_f, indent=2)
        
    with open(cn_out_json, 'w', encoding='utf-8') as out_f:
        json.dump(normalized_data["container_data"], out_f, indent=2)
        
    print(f"\n[+] Success! BL Data exported to: {bl_out_json}")
    print(f"[+] Success! Container Data exported to: {cn_out_json}")
        
    return normalized_data

def print_extraction_report(normalized_data):
    bl_table = normalized_data["bl_data"]
    cn_table = normalized_data["container_data"]
    
    excel_bls = len(bl_table)
    excel_containers = len(cn_table)
    
    extracted_bl_count = sum(1 for bl in bl_table if bl.get("raw_bl_text", "").strip())
    
    extracted_text_count = sum(
        1 for cn in cn_table 
        if next((bl for bl in bl_table if bl["bl_number"] == cn["bl_number"]), {}).get("raw_bl_text", "").strip()
    )
    
    print("\n EXTRACTION REPORT:")
    print(f" > Excel BL count:              {excel_bls}")
    print(f" > Extracted BL count:          {extracted_bl_count}")
    print(f" > Excel container count:       {excel_containers}")
    print(f" > Extracted container count:   {extracted_text_count}")
    
    if excel_containers > 0:
        success_rate = (extracted_text_count / excel_containers) * 100
        print(f" > Success Rate:                {success_rate:.1f}%")

if __name__ == "__main__":
    # Go up 3 levels from parsers/msc/parser.py to get to the root of the repo
    root_dir = Path(__file__).resolve().parent.parent.parent
    
    # Inputs
    PDF_FILE = root_dir / "data" / "inputs" / "MSC ANA CAMILA III ZA622A TINCAN  PDF.pdf"
    
    # NOTE: Ensure this matches the exact name of the file sitting in data/inputs/
    EXCEL_FILE = root_dir / "data" / "inputs" / "MSC ANA CAMILA III ZA622A TINCAN  PDF.CAL.xlsx"
    
    # Outputs (Routed to the new organized folders)
    MD_FILE = root_dir / "data" / "outputs" / "md" / "output_msc.md"
    STAGED_BL_JSON = root_dir / "data" / "outputs" / "json" / "staged_bls.json"
    STAGED_CN_JSON = root_dir / "data" / "outputs" / "json" / "staged_containers.json"
    
    # AI Exports
    GEMINI_JSON = root_dir / "data" / "outputs" / "json" / "final_data_gemini.json"
    OPENAI_JSON = root_dir / "data" / "outputs" / "json" / "final_data_openai.json"
    SIMULATION_JSON = root_dir / "data" / "outputs" / "json" / "final_data_simulation.json"
    OLLAMA_JSON = root_dir / "data" / "outputs" / "json" / "final_data_ollama.json"
    
    # Define Target Excel Output Directory
    EXCEL_DIR = root_dir / "data" / "outputs" / "excel"
    
    ACTIVE_AI_PROVIDERS = ["ollama"]
    
    try:
        # Phase 0: Convert PDF to Markdown dynamically
        print("\n" + "="*45)
        print(" PHASE 0: PDF to MARKDOWN CONVERSION")
        print("="*45)
        convert_pdf_to_md(PDF_FILE, MD_FILE)

        # Phase 1: Generates staged_bls.json and staged_containers.json
        staged_data = run_staging_phase(EXCEL_FILE, MD_FILE, STAGED_BL_JSON, STAGED_CN_JSON)
        
        print_extraction_report(staged_data)
        
        # Phase 2: AI Generates final_data_ollama.json (Strictly BL Level Schema)
        if ACTIVE_AI_PROVIDERS:
            # We cast paths to str() just to be safe with the ai_pipeline parameters
            ai_pipeline.run_ai_phase(
                staged_data, 
                str(GEMINI_JSON), 
                str(OPENAI_JSON), 
                str(SIMULATION_JSON), 
                str(OLLAMA_JSON), 
                ACTIVE_AI_PROVIDERS
            )
        else:
            print("\n" + "="*45)
            print(" PHASE 2: AI EXTRACTION SKIPPED")
            print("="*45)
            print(f" [!] Pipeline finished successfully with Staged Data only.")
            
        # Phase 3: Export to Excel
        print("\n" + "="*45)
        print(" PHASE 3: EXPORT TO EXCEL")
        print("="*45)
        
        # Build the list of files to convert based on what ran
        files_to_convert = [str(STAGED_BL_JSON), str(STAGED_CN_JSON)]
        if ACTIVE_AI_PROVIDERS:
            files_to_convert.append(str(OLLAMA_JSON))
            
        convert_json_to_excel(files_to_convert, str(EXCEL_DIR))
            
    except FileNotFoundError as e:
        print(f"\n❌ File Error: Could not find a required input file.\n{e}")
        print("Please check your data/inputs/ folder.")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")