from pathlib import Path
from document_image_extractor.config import load_config
from document_image_extractor.pipeline import list_input_files, process_file
from document_image_extractor.report import print_file_report, accumulate_totals, print_summary
from document_image_extractor.utils.files import ensure_dir

def main():
    cfg = load_config()
    paths = cfg["paths"]

    input_dir = Path(paths["input_dir"])
    output_dir = Path(paths["output_dir"])
    temp_dir = Path(paths["temp_dir"])
    ensure_dir(input_dir)
    ensure_dir(output_dir)
    ensure_dir(temp_dir)

    files = list_input_files(input_dir)

    if not files:
        print(f"⚠️ No se encontraron archivos .pdf o .docx en: {input_dir.resolve()}")
        return
    
    total = {"found": 0, "saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}
    skipped = 0
    failed = 0

    for f in files:
        stats = process_file(f, cfg)
        print_file_report(f.name, stats)

        if stats.get("skipped"):
            skipped += 1
            continue

        if "error" in stats:
            failed += 1
            continue

        accumulate_totals(total, stats)
    
    print_summary(files=len(files), skipped=skipped, failed=failed, total=total)

if __name__== "__main__":
    main()