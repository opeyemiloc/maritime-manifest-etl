
# # cargo.py
# import re
# from models import Container

# class CargoRefiner:
#     def __init__(self):
#         self.noise_patterns = [
#             # 1. Standard manifest noise & Internal codes
#             re.compile(r'^Tare Weight:', re.IGNORECASE),
#             re.compile(r'^Harmonized Code:', re.IGNORECASE),
#             re.compile(r'^(SHIPPER|CONSIGNEE|NOTIFY ADDRESS)', re.IGNORECASE),
#             re.compile(r'^(SH:|CO:|NF:|EW:|B/L NR\.)'),
#             re.compile(r'^Total number of containers:', re.IGNORECASE),
#             re.compile(r'^Total on this bill of lading:', re.IGNORECASE),
#             re.compile(r'^\d{2}-\d{3}[A-Z]+$'), 
            
#             # 2. Combined OR Standalone Weights and Measurements
#             # -> NEW: The number in front is now optional `?`. This catches "kgs." by itself!
#             re.compile(r'^([\d.,]+\s*)?(kgs\.?|lbs\.?|cu\.\s*m\.|cu\.\s*ft\.|packages)$', re.IGNORECASE),
#             re.compile(r'^[\d.,]+$'), 
            
#             # 3. Summary Container Sizes & Package Totals
#             re.compile(r"^(?:\d+\s*x\s*)?\d+'\s*(HIGH CUBE|DRY VAN|HC|DV)$", re.IGNORECASE),
#             re.compile(r"^\d+\s*PACKAGE\(S\)$", re.IGNORECASE), 
            
#             # 4. Global Address & Company Bouncer
#             re.compile(r'^(TO THE ORDER OF|BANK PLC)'),
#             re.compile(r'(S\.A\. DE C\.V\.|PLC|LTD\.|LIMITED|FZCO|TRADE SERVICES SA)$', re.IGNORECASE),
#             re.compile(r'^Phone No\s*:'),
#             re.compile(r'^Fax No\s*:'),
#             re.compile(r'^(PLOT\s*\d+|P\.?M\.?B\.?\s*\d+|P\.?O\.?\s*Box)'),
#             re.compile(r'^(Ikeja|Lagos|Dubai, UAE)$', re.IGNORECASE),
#             re.compile(r'Miguel Hidalgo, Mexico', re.IGNORECASE),
            
#             # 5. Street / Location / Geography Keywords
#             re.compile(r'(STREET|AVENUE|BLVD|ROAD|DISTRICT|EXPRESSWAY|FREEZONE|BUILDING NO|OFFICE NO)', re.IGNORECASE),
#             re.compile(r'(ALICIA ARCINIEGA|TORRE SUR|COL\. GRANADA|SAAVEDRA|VICTORIA ISLAND)', re.IGNORECASE),
#             re.compile(r'(Ilupeju|RUE SOLVAY|Jemeppe|MAKUN CITY|JEBEL ALI|Lagos\s*\d+)', re.IGNORECASE)
#         ]

#     def refine(self, raw_container_dict: dict) -> Container:
#         clean_cargo = []
#         for line in raw_container_dict["raw_cargo_lines"]:
#             line = line.strip()
#             if line and not any(pattern.search(line) for pattern in self.noise_patterns):
#                 clean_cargo.append(line)
                
#         return Container(
#             container_number=raw_container_dict["container_number"],
#             seals=raw_container_dict["seals"],
#             cargo_description=clean_cargo
#         )
    