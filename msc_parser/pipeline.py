import json
from excel_reader import ExcelCartographer
from cleaner import MarkdownCleaner
from segmenter import PDFSegmenter

def process_manifest(excel_filepath: str, markdown_filepath: str) -> dict:
    cartographer = ExcelCartographer()
    cleaner = MarkdownCleaner()
    segmenter = PDFSegmenter()
    
    # 1. Build the foundational map from Excel
    bl_map = cartographer.build_map(excel_filepath)
    
    # 2. Read the raw Markdown PDF conversion
    with open(markdown_filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()
        
    # 3. Clean noise and extract chronological text blocks
    clean_lines = cleaner.clean(raw_text)
    final_bl_map = segmenter.snipe_text(bl_map=bl_map, clean_lines=clean_lines)
    
    bl_table = []
    container_table = []
    
    # 4. Split the mapped data into Two Normalized Tables
    for bl in final_bl_map.values():
        # TABLE 1: Staged BL Table (Now holds consignee & hs_code directly!)
        bl_table.append({
            "bl_number": bl.bl_number,
            "consignee": bl.consignee,
            "raw_bl_text": bl.raw_bl_text,
            "hs_code": bl.hs_code,
            "form_m": bl.form_m
        })
        
        # TABLE 2: Staged Container Table (Preserves pure physical data & position)
        for c in bl.containers:
            container_table.append({
                "bl_number": bl.bl_number,
                "container_number": c.container_number,
                "size_type": c.size_type,
                "seals": c.seals,
                "pdf_position": c.pdf_position
            })
            
    return {
        "bl_data": bl_table,
        "container_data": container_table
    }