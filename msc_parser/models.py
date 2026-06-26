import json
from dataclasses import dataclass, field, asdict

@dataclass
class Container:
    container_number: str
    size_type: str = ""
    seals: list[str] = field(default_factory=list)
    pdf_position: int = 999  # Preserved for the Container Staging Table!

@dataclass
class BillOfLading:
    bl_number: str
    consignee: str = ""
    raw_bl_text: str = "" 
    
    # Extracted BL-level fields
    product_name: str = ""
    hs_code: str = ""
    form_m: str = ""
    customs_category: str = ""
    
    containers: list[Container] = field(default_factory=list)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (BillOfLading, Container)):
            return asdict(o)
        return super().default(o)