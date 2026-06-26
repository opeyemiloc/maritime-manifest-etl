import os
import pandas as pd
from models import BillOfLading, Container

class ExcelCartographer:
    def __init__(self):
        # The exact column names based on your Excel upload (RESTORED)
        self.col_bl = "Bill of Lading Number"
        self.col_cn = "Container Number"
        self.col_size = "Size/Type"
        self.col_seal = "Seal Nbrs"
        self.col_consignee = "Consignee Name"

    def build_map(self, filepath: str) -> dict[str, BillOfLading]:
        """Reads an Excel (or CSV) file and returns a dictionary mapping BL Numbers to BillOfLading objects."""
        bl_map = {}
        
        # Check file extension to use the correct pandas reader
        _, ext = os.path.splitext(filepath)
        
        try:
            if ext.lower() == '.csv':
                # Skip the first 5 rows of metadata to reach the headers
                df = pd.read_csv(filepath, skiprows=5)
            else:
                # Natively read the .xlsx file
                df = pd.read_excel(filepath, engine='openpyxl', skiprows=5)
        except Exception as e:
            raise RuntimeError(f"Failed to read the file {filepath}. Error: {e}")

        # Clean the data: Convert all NaN/Null values to empty strings to prevent crashes
        df = df.fillna("")
        
        # Ensure we actually found the right header row
        if self.col_bl not in df.columns:
            raise ValueError(f"Could not find the correct header '{self.col_bl}' in the document. Check the skiprows count.\nActual columns found: {list(df.columns)}")
            
        # Iterate through the rows using pandas
        for _, row in df.iterrows():
            bl_number = str(row.get(self.col_bl, "")).strip()
            cn_number = str(row.get(self.col_cn, "")).strip()
            
            # Skip empty/invalid rows
            if not bl_number or not cn_number:
                continue
            
            # If this is a new BL, initialize it in our map
            if bl_number not in bl_map:
                # NEW HYBRID LOGIC: Capture Consignee immediately at the BL level!
                bl_map[bl_number] = BillOfLading(
                    bl_number=bl_number,
                    consignee=str(row.get(self.col_consignee, "")).strip()
                )
            
            # Handle seals (Sometimes separated by spaces or 'NA' in your data)
            raw_seals = str(row.get(self.col_seal, "")).strip()
            clean_seals = [s for s in raw_seals.split() if s and s.upper() != "NA"]
            
            # NEW HYBRID LOGIC: Create the container (Physical details ONLY)
            new_container = Container(
                container_number=cn_number,
                size_type=str(row.get(self.col_size, "")).strip(),
                seals=clean_seals
            )
            
            # Attach container to the BL
            bl_map[bl_number].containers.append(new_container)
                
        return bl_map