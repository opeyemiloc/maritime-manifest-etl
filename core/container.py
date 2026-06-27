# container.py
import re

class ContainerSegmenter:
    def __init__(self):
        self.cn_pattern = re.compile(r'^CN:\s*([A-Z]{4}\d{7})')
        self.seal_pattern = re.compile(r'^SN:\s*(.*)')

    def segment(self, bl_lines: list[str]) -> list[dict]:
        containers = []
        current_container = None
        
        for line in bl_lines:
            cn_match = self.cn_pattern.match(line)
            
            # New Container Found
            if cn_match:
                current_container = {
                    "container_number": cn_match.group(1),
                    "seals": [],
                    "raw_cargo_lines": []
                }
                containers.append(current_container)
                continue
                
            # If we are inside a container chunk, look for seals or cargo
            if current_container is not None:
                seal_match = self.seal_pattern.match(line)
                if seal_match:
                    current_container["seals"].append(seal_match.group(1))
                elif line.startswith('INT') and len(line) == 8:
                    # Edge case: standalone seals on next line
                    current_container["seals"].append(line)
                else:
                    # Everything else is dumped into raw cargo for the next step
                    current_container["raw_cargo_lines"].append(line)
                    
        return containers