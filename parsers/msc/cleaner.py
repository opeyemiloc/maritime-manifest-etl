# cleaner.py
import re

class MarkdownCleaner:
    def __init__(self):
        # These patterns target the repeating page headers, standard table columns, and titles
        self.header_patterns = [
            re.compile(r'\\f'),
            re.compile(r'Page \d+ of \d+', re.IGNORECASE),
            re.compile(r'^(MEDITERRANEAN|SHIPPING COMPANY|S\.A\., Geneva)$'),
            
            # --- NEWLY ADDED: Kills the leftover title ---
            re.compile(r'^CARGO MANIFEST$', re.IGNORECASE), 
            
            re.compile(r'^1a\.- NAME OF SHIP'),
            re.compile(r'^1b\.-VOYAGE'),
            re.compile(r'^MSC [A-Z\s]+(?:\(\d+\))?$'), # Catches "MSC ORIANE (6074)"
            re.compile(r'^(NY\d+[A-Z]?)$'),            # Catches Voyage "NY448A"
            re.compile(r'^BILL ISSUANCE'),
            re.compile(r'^3\.- NATIONALITY OF SHIP'),
            re.compile(r'^PLACE OF RECEIPT'),
            re.compile(r'^5[ab]\. PORT OF'),
            re.compile(r'^DEPARTURE DATE'),
            re.compile(r'^Date Of Arrival'),
            re.compile(r'^FINAL DESTINATION'),
            re.compile(r'^\(not required in U\.S\.\)'),
            re.compile(r'^Transshipment:'),
            re.compile(r'^6\.- \s*MARKS AND NRS'),
            re.compile(r'^Service Contract'),
            re.compile(r'^CONTAINER\s+NRS'),
            re.compile(r'^NRS\.\s*\(SN\)'),
            re.compile(r'^7\.- NUMBER AND KIND'),
            re.compile(r'^DESCRIPTION OF GOODS'),
            re.compile(r'^\(ANSWER COL\. 8 OR COL\. 9\)'),
            re.compile(r'^8 -GROSS WEIGHT'),
            re.compile(r'^\(LB\. OR KG\.\)'),
            re.compile(r'^9 - MEASURMENT'),
            re.compile(r'^\(PER TEUS\)'),
            re.compile(r'^\d{2} [A-Z][a-z]{2} \d{4}$'),  # Catches Dates like "10 Nov 2024"
            
            # Known Location Noise in your specific document
            re.compile(r'^(Panama|Lagos, , NG|TINCAN/LAGOS|Mexico|Belgium)$', re.IGNORECASE),
            re.compile(r'^(ALTAMIRA\s*TAM,|ANTWERP|ANTWERP\s*VAN,)$', re.IGNORECASE)
        ]

    def clean(self, raw_text: str) -> list[str]:
        cleaned_lines = []
        for line in raw_text.split('\n'):
            line = line.strip()
            
            if not line:
                continue
                
            # If the line matches ANY of the header patterns, throw it in the trash
            if any(pattern.search(line) for pattern in self.header_patterns):
                continue
                
            cleaned_lines.append(line)
            
        return cleaned_lines