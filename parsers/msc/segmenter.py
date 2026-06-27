import re
from models import BillOfLading

class PDFSegmenter:
    def __init__(self):
        # Boundaries for the "BL Block" folder
        self.bl_start_pattern = re.compile(r'^(MEDU[A-Z0-9]{8})$')
        self.bl_summary_pattern = re.compile(r'^(Total number of containers|Total on this bill of lading)', re.IGNORECASE)
        self.container_pattern = re.compile(r'^(?:CN:\s*)?([A-Z]{4}\d{7})$')
        
        # Free Regex Layer
        self.hs_pattern = re.compile(r'(?:Harmonized|Harmonised|HS)\s*Code[s]?\s*[:\-]?\s*(\d{4,12})', re.IGNORECASE)
        self.form_m_pattern = re.compile(r'(MF\d{9,12}|BA\d{9,12})', re.IGNORECASE)

    def snipe_text(self, bl_map: dict[str, BillOfLading], clean_lines: list[str]) -> dict[str, BillOfLading]:
        bl_blocks = {}
        active_bl = None
        start_idx = 0
        
        # ==========================================
        # 1. Identify and Slice the BL Blocks
        # ==========================================
        for i, line in enumerate(clean_lines):
            bl_match = self.bl_start_pattern.match(line)
            if bl_match:
                if active_bl:
                    bl_blocks[active_bl] = clean_lines[start_idx:i]
                active_bl = bl_match.group(1)
                start_idx = i
                continue
                
            if active_bl and self.bl_summary_pattern.search(line):
                bl_blocks[active_bl] = clean_lines[start_idx:i+1]
                active_bl = None
                
        # Catch any trailing active BL at the very end of the document
        if active_bl:
            bl_blocks[active_bl] = clean_lines[start_idx:]

        # ==========================================
        # 2. Extract Data & Apply Directly to Models
        # ==========================================
        for bl_id, lines in bl_blocks.items():
            if bl_id not in bl_map:
                continue
                
            raw_text = "\n".join(lines).strip()
            bl_map[bl_id].raw_bl_text = raw_text 
            
            # --- FREE REGEX LAYER (Applied directly to the BL) ---
            hs_matches = list(set(self.hs_pattern.findall(raw_text)))
            form_m_matches = list(set(self.form_m_pattern.findall(raw_text)))
            
            bl_map[bl_id].hs_code = " | ".join(hs_matches)
            bl_map[bl_id].form_m = " | ".join(form_m_matches)

            # --- POSITIONAL TRACKING FOR CONTAINERS (Preserved for Database Normalization) ---
            position_counter = 1
            for line in lines:
                cn_match = self.container_pattern.search(line)
                if cn_match:
                    found_cn = cn_match.group(1)
                    # Find the corresponding container in our Excel map and stamp its PDF position
                    for container in bl_map[bl_id].containers:
                        if container.container_number == found_cn and container.pdf_position == 999:
                            container.pdf_position = position_counter
                            position_counter += 1
                            break

        return bl_map