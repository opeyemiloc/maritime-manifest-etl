# Maritime Manifest ETL Pipeline

## 📌 Project Overview

This project is an automated ETL (Extract, Transform, Load) pipeline designed to extract crucial customs and cargo data from complex, unstructured maritime PDF manifests.

The primary business objective is to identify  **what commodities are entering the port on a per-Bill-of-Lading (BL) basis** . Specifically, the pipeline extracts:

1. Physical Product Names (e.g., "FRESH APPLES")
2. Harmonized System (HS) Codes
3. Form M Numbers / BA Numbers

By pairing a "Master Map" (from Excel) with the unstructured PDF manifest, the pipeline maps specific commodities to their overarching contracts (Bills of Lading), drastically reducing the manual labor of customs data entry.

## 🧠 The Business Logic Evolution

Building this pipeline required adapting to the messy, unstructured reality of maritime shipping documents. The core extraction logic evolved through three distinct phases:

### Phase 1: The "Pure Regex" Era (Deprecated `cargo.py`)

Initially, the pipeline attempted to clean and extract cargo descriptions using brute-force regular expressions.

* **The Logic:** A `CargoRefiner` was built with massive lists of noise patterns to filter out weights, addresses, and page artifacts line-by-line.
* **The Result:** It was too brittle. Maritime manifests are chaotic; a slight typo in an address or a weirdly formatted Tare weight would bypass the rules and pollute the data. It required endless maintenance.

### Phase 2: The "Container-Centric" AI Trap

Realizing Regex wasn't smart enough to read the raw cargo text, Large Language Models (AI) were introduced. The logic attempted to extract text  **container-by-container** , feeding small chunks to the AI.

* **The Problem:** Standard PDF-to-Text conversion tools (like Markitdown) read PDFs in blocks, effectively scrambling visual columns into horizontal lists. Container numbers would stack at the top of a page, and all the cargo descriptions would stack at the bottom.
* **The Result:** The script would cut off prematurely, leaving containers "empty" and swallowing the cargo data. Furthermore, making 1 API call *per container* was extremely slow and expensive.

### Phase 3: The "BL-Centric" Masterplan (Current)

We completely pivoted the business logic to match maritime reality: **The Bill of Lading (BL) is the master contract.** Customs clears the BL, and HS Codes/Form Ms apply to the BL as a whole.

* **The Solution:** Instead of chopping the document by containers, we treat the entire BL as a "Folder." The script finds the start of the BL (`MEDU...`) and the end summary line (`Total number of containers:`), and snipes that  *entire, massive block of text* .
* **The Result:** Zero data loss. Page breaks and stacked containers no longer break the system. We use fast, free Regex to grab structured data (HS Codes) from the block, and we send the rest to the AI. API calls were reduced by 50% (1 call per BL instead of 1 per container).

## 🏗️ Pipeline Architecture (How it Works)

The current pipeline operates in 5 distinct phases:

1. **The Master Map (Excel):** Reads the structured Excel file to know exactly which Containers belong to which Bills of Lading.
2. **The PDF Scan & Track:** Reads the converted PDF Markdown file. It locates the "BL Blocks" (the folders) and records the *exact chronological position/order* of the containers as they appear in the PDF. (This future-proofs the system in case we ever need to strictly match Commodity #1 to Container #1).
3. **The Sniper Extraction:** Extracts the massive, raw text block for each BL, ignoring the scrambled columns.
4. **The Free Regex Layer (Structured Data):** Searches purely within the isolated BL Block for exact keywords (e.g., `Harmonized Code:`, `MF...`) to extract HS Codes and Form M numbers *without* spending AI credits.
5. **The AI Brain (Unstructured Data):** Passes the BL Block to a Large Language Model (Google Gemini, OpenAI, or Local Ollama) with a strict prompt to extract and clean the physical Product Names, returning them in a flat, structured JSON list.

## 🛠️ Architectural Design: Why Raw REST APIs?

You might notice that this pipeline uses Python's standard `requests` library to communicate with OpenAI and Google Gemini, rather than installing their official Python SDKs (e.g., `pip install openai google-genai`). This is an intentional architectural choice based on four factors:

1. **Zero Extra Dependencies:** By relying purely on HTTP REST API calls, the project stays incredibly lightweight. There is no need to manage or constantly update massive 3rd-party vendor packages that might break backward compatibility over time.
2. **Absolute Control Over Rate Limiting:** When dealing with massive documents, APIs frequently return a `429 Too Many Requests` error. SDKs often hide these behind complex, proprietary exceptions. Using raw requests allows us to implement one universal exponential backoff loop based purely on standard HTTP status codes.
3. **Architectural Symmetry:** Local AI (Ollama) inherently communicates via local REST APIs. By treating Gemini and OpenAI as simple REST endpoints as well, our Extractor module maintains the exact same predictable pattern (Build Payload -> POST -> Check Status -> Parse JSON) seamlessly across all providers.
4. **Raw Debugging Power:** Direct access to HTTP status codes (like `404 Not Found` or `403 Forbidden`) and raw server response text makes debugging issues like missing API keys or incorrectly typed model names immediately transparent.

## 🚀 Future Roadmap

* Implement the Positional Tracking feature to bind specific products back to specific containers based on their chronological appearance in the BL Block.
* Expand the Regex layer to capture specific package quantities and weights.
