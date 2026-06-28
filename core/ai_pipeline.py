import json
import os
import copy
from dotenv import load_dotenv
from core.ai_extractor import CargoAIExtractor

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def _execute_ai_model(extractor, raw_parsed_data, output_filepath, provider_name):
    print(f"\n >>> Running {provider_name.upper()} Extraction...")
    
    data_copy = copy.deepcopy(raw_parsed_data)
    # The AI engine completely ignores the Container Table and strictly reads the BL Table!
    bl_table = data_copy["bl_data"] 
    
    bl_level_export = []
    ai_processed_count = 0
    
    for bl in bl_table:
        text = bl.get("raw_bl_text", "").strip()
        if not text:
            continue
            
        consignee = bl.get("consignee", "")
        ai_results = extractor.extract(text)
        
        joined_products = ""
        regex_hs = bl.get("hs_code", "")
        final_hs = regex_hs
        
        if ai_results:
            ai_processed_count += 1
            # Merge all identified products into a single row using the pipe delimiter
            joined_products = " | ".join([item.get("product_name", "") for item in ai_results if item.get("product_name")])
            
            # If the AI discovers HS codes, we use them to supplement the regex fallback
            ai_hs_codes = " | ".join([item.get("hs_code", "") for item in ai_results if item.get("hs_code")])
            if ai_hs_codes:
                final_hs = ai_hs_codes
            
        # The clean flat JSON schema precisely as requested
        flat_record = {
            "bl_number": bl.get("bl_number", ""),
            "consignee": consignee,
            "product_name": joined_products,
            "hs_code": final_hs,
            "customs_category": bl.get("customs_category", "")
        }
        
        bl_level_export.append(flat_record)

    with open(output_filepath, 'w', encoding='utf-8') as out_f:
        json.dump(bl_level_export, out_f, indent=2)
        
    print(f"     [+] Completed! {ai_processed_count} Bills of Lading processed. Saved to: {output_filepath}")

def run_ai_phase(parsed_data, gemini_out, openai_out, sim_out, ollama_out=None, active_providers=None):
    print("\n" + "="*45)
    print(" PHASE 2: AI EXTRACTION (BL-Centric)")
    print("="*45)
    
    if active_providers is None:
        active_providers = []

    ran_any = False
    
    if "gemini" in active_providers and GEMINI_API_KEY:
        gemini_bot = CargoAIExtractor(api_key=GEMINI_API_KEY, provider="gemini")
        _execute_ai_model(gemini_bot, parsed_data, gemini_out, "Google Gemini (1.5 Flash)")
        ran_any = True
        
    if "openai" in active_providers and OPENAI_API_KEY:
        openai_bot = CargoAIExtractor(api_key=OPENAI_API_KEY, provider="openai")
        _execute_ai_model(openai_bot, parsed_data, openai_out, "OpenAI (GPT-4o-mini)")
        ran_any = True

    if "ollama" in active_providers and ollama_out:
        ollama_bot = CargoAIExtractor(provider="ollama")
        _execute_ai_model(ollama_bot, parsed_data, ollama_out, "Ollama (Local llama3.2:3b)")
        ran_any = True
        
    if "simulation" in active_providers or (not ran_any and len(active_providers) > 0):
        print("\n [!] Running in Simulation Mode...")
        sim_bot = CargoAIExtractor(provider="simulation")
        _execute_ai_model(sim_bot, parsed_data, sim_out, "Simulator")