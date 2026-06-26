import json
import re
import requests
import time

class CargoAIExtractor:
    def __init__(self, api_key="", provider="simulation", delay_between_calls=2.0):
        self.api_key = api_key
        self.provider = provider.lower()
        self.delay = delay_between_calls
        
    def _build_prompt(self, text: str) -> str:
        return f"""
        You are an expert Nigerian Customs Data Extractor.
        You are given the raw, scrambled text of an entire Bill of Lading.
        
        YOUR MISSION:
        Extract a chronological list of physical product commodities AND their corresponding HS Codes found in this text.
        
        RULES:
        1. Extract ONLY the physical product names actually present in the text. DO NOT invent, guess, or add any products.
        2. Extract the associated HS Code (often labeled as "Harmonized Code" or "HS Code") for each product. If there is no code, leave it blank.
        3. Ignore container sizes, company names, weights, and addresses.
        4. Return them as an ordered list in the JSON schema below.
        
        Respond STRICTLY in valid JSON format matching this exact schema:
        {{
            "items": [
                {{
                    "product_name": "string",
                    "hs_code": "string"
                }}
            ]
        }}
        
        TEXT TO ANALYZE:
        {text}
        """

    def extract(self, raw_text: str) -> list[dict]:
        if not raw_text or not raw_text.strip():
            return []

        if self.provider == "simulation" or (self.provider != "ollama" and (not self.api_key or self.api_key == "YOUR_API_KEY")):
            return self._simulate_ai_extraction(raw_text)
            
        prompt = self._build_prompt(raw_text)
        
        if self.provider == "openai":
            time.sleep(self.delay)
            return self._extract_openai(prompt)
        elif self.provider == "gemini":
            time.sleep(self.delay)
            return self._extract_gemini(prompt)
        elif self.provider == "ollama":
            return self._extract_ollama(prompt)
        else:
            return []
            
    def _extract_ollama(self, prompt: str) -> list[dict]:
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": "llama3.2:3b", 
            "messages": [{"role": "user", "content": prompt}],
            "format": "json", 
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"      [!] Ollama Error {response.status_code}: {response.text.strip()}")
                return []
            ai_json_string = response.json()['message']['content']
            return self._parse_json_safely(ai_json_string)
        except Exception as e:
            print(f"      [!] Ollama Connection Error: {e}")
            return []

    def _extract_openai(self, prompt: str) -> list[dict]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "gpt-4o-mini", "response_format": { "type": "json_object" }, "messages": [{"role": "user", "content": prompt}]}
        
        delays = [1, 2, 4, 8, 16]
        for attempt in range(len(delays) + 1):
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if response.status_code == 429 and attempt < len(delays):
                    time.sleep(delays[attempt])
                    continue
                if response.status_code != 200:
                    return []
                ai_json_string = response.json()['choices'][0]['message']['content']
                return self._parse_json_safely(ai_json_string)
            except Exception as e:
                return []
        return []

    def _extract_gemini(self, prompt: str) -> list[dict]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
        
        delays = [1, 2, 4, 8, 16]
        for attempt in range(len(delays) + 1):
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 429 and attempt < len(delays):
                    time.sleep(delays[attempt])
                    continue
                if response.status_code != 200:
                    return []
                ai_json_string = response.json()['candidates'][0]['content']['parts'][0]['text']
                return self._parse_json_safely(ai_json_string)
            except Exception as e:
                return []
        return []

    def _parse_json_safely(self, json_string: str) -> list[dict]:
        try:
            clean_string = re.sub(r'```json\n|\n```|```', '', json_string).strip()
            parsed = json.loads(clean_string)
            items = parsed.get("items", parsed.get("commodities", []))
            
            clean_results = []
            for item in items:
                clean_results.append({
                    "product_name": str(item.get("product_name", "")).strip(),
                    "hs_code": str(item.get("hs_code", "")).strip()
                })
            return clean_results
        except json.JSONDecodeError as e:
            return []

    def _simulate_ai_extraction(self, text: str) -> list[dict]:
        product = "UNKNOWN CARGO"
        hs = ""
        if "PEARS" in text.upper(): product = "FRESH PEARS"
        elif "STEEL" in text.upper(): product = "STEEL PRODUCTS"
        elif "APPLES" in text.upper(): product = "FRESH APPLES"
            
        hs_match = re.search(r'Harmonized Code:\s*(\d{6,10})', text, re.IGNORECASE)
        if hs_match: hs = hs_match.group(1)
        return [{"product_name": product, "hs_code": hs}]