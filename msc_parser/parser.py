import json
import os
from pipeline import process_manifest
from ai_pipeline import run_ai_phase

def run_staging_phase(excel_filepath, md_filepath, bl_out_json, cn_out_json):
    print("\n" + "="*45)
    print(" PHASE 1: DATA STAGING & NORMALIZATION")
    print("="*45)
    
    normalized_data = process_manifest(excel_filepath, md_filepath)
    
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    EXCEL_FILE = os.path.join(parent_dir, "MSC ANA CAMILA III ZA622A TINCAN  PDF.CAL.xlsx")
    MD_FILE = os.path.join(parent_dir, "output_msc.md")
    
    # We maintain BOTH Staged files
    STAGED_BL_JSON = os.path.join(parent_dir, "staged_bls.json")
    STAGED_CN_JSON = os.path.join(parent_dir, "staged_containers.json")
    
    # AI Exports
    GEMINI_JSON = os.path.join(parent_dir, "final_data_gemini.json")
    OPENAI_JSON = os.path.join(parent_dir, "final_data_openai.json")
    SIMULATION_JSON = os.path.join(parent_dir, "final_data_simulation.json")
    OLLAMA_JSON = os.path.join(parent_dir, "final_data_ollama.json")
    
    ACTIVE_AI_PROVIDERS = ["ollama"]
    
    try:
        # Phase 1: Generates staged_bls.json and staged_containers.json
        staged_data = run_staging_phase(EXCEL_FILE, MD_FILE, STAGED_BL_JSON, STAGED_CN_JSON)
        
        print_extraction_report(staged_data)
        
        # Phase 2: AI Generates final_data_ollama.json (Strictly BL Level Schema)
        if ACTIVE_AI_PROVIDERS:
            run_ai_phase(staged_data, GEMINI_JSON, OPENAI_JSON, SIMULATION_JSON, OLLAMA_JSON, ACTIVE_AI_PROVIDERS)
        else:
            print("\n" + "="*45)
            print(" PHASE 2: AI EXTRACTION SKIPPED")
            print("="*45)
            print(f" [!] Pipeline finished successfully with Staged Data only.")
            
    except FileNotFoundError as e:
        print(f"File Error: Check your parent folder.\n{e}")
    except Exception as e:
        print(f"Error during execution: {e}")