# Document-Image-Extractor

CLI tool to extract embedded images from **DOCX**, **PDF**, **PPTX** and **XLSX** files, with deduplication , size filtering, and batch export to ZIPs.

---

## Features:
Extract images from: 
- DOCX (Word documents)
- PDF (documents)
- PPTX (Powerpoint documents)
- XLSX (Excel documents)

Outputs:
- Creates a **ZIP per input file** with extracted images

built-in helpers:
- **Deduplication** (skips repeated images within the same document)
- **Size filter** (`min_kb` default is 5kb)
- Handles “no images” and **corrupt files** gracefully

---

## Project status
this repository is begin improved **phase by phase** 

---

## Requirements
- python 3.12+ (recomended)

Dependencies (install from 'requirements.txt'):
- python-docx
- PyMuPDF
- pillow

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/LeoMurilloDev/document-image-extractor.git
cd document-image-extractor 
```

### 2. Create and activate a virtual environment
#### Windows
```bash
python -m  venv .venv
.\.venv\Scripts\activate
```
#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
pip install -r requirements.txt

## Usage

### Folder structure expected by the script 
the script creates these folders automatically if they don't exist:
- **Entrdas_archivos/** -> place your **.docx** and **.pdf** files here
- **Salidas_archivos/** -> output ZIPs will be generated here
- **temp/** -> temporary extraction folder (auto-cleaned)

### Configuration 
You can customize filters without editing the code using `config.json` (repo root).
Example: 
```json
{
  "filters": {
    "min_kb": 5,
    "min_width": 0,
    "min_height": 0
  }
}
```
- `min_kb`: minimum file size in kb (default: 5)
- `min_width`/ `min_height`: optional dimension filter (0 disables it)


## Run 
```bash
python main.py
```

## CLI usage
The tool can be used with default folders/config:

```bash
python main.py

python main.py --input Entradas_archivos --output Salidas_archivos

python main.py --input example.pptx --output Salidas_archivos

python main.py --input Entradas_archivos --recursive

python main.py --input Entradas_archivos --min-kb 1 --min-width 100 --min-height 100

python main.py --input Entradas_archivos --no-dedup

python main.py --input Entradas_archivos --format folder

python main.py --input Entradas_archivos --log-level DEBUG --log-file logs/debug.log
```

## Output
- For each input file, a ZIP is created in **Salidas_archivos/**
- Example: 
    - Input: **Entradas_archivos/report.pdf**
    - Output: **Salidas_archivos/report.zip**

## What to expect
When you run the script, it prints a summary per file:
- `guardadas` -> images saved successfully
- `duplicadas` -> images skipped due to hash duplication
- `pequeñas` -> images filtered out by size
- `encontradas` -> images found inside the document
### Important notes
- In `DOCX`, images are saved using the real extension (.jpg, .png, .gif, etc)
- `temp/` is cleaned even when a file fails

## Test suites
we use small test suites to validate.
### Documents to try
Includes:
- Mixed formats (JPG/PNG/GIF)
- Duplicates
- Small icon filtered out by size
- Corrupt files (error handling)
Manual validation steps: 
1. Copy test files into `Entradas_archivos/`
2. Run `python main.py`
3. Verify
    - Output ZIPs exist in `Salidas_archivos/`
    - Extencions are correct in DOCX resutls (.jpg, .png, .gif)
    - Duplicates are removed
    - `temp/` is empty at the end

## Contributing
if you want to propose changes:
1. Fork the repo 
2. Create a branch
3. Open a PR with a clear description