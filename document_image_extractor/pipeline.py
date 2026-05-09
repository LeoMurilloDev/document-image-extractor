from pathlib import Path
from typing import Any, Dict, List
from .extractors.docx_extractor import extract_docx_images
from .extractors.pdf_extractor import extract_pdf_images
from .extractors.pptx_extractor import extract_pptx_images
from .extractors.xlsx_extractor import extract_xlsx_images
from .utils.files import clean_dir, ensure_dir, create_zip_from_folder, copy_folder

SUPPORTED_EXTS = {".pdf", ".docx", ".pptx", ".xlsx"}

def process_file(file_path: Path, cfg: Dict[str, Any]) -> Dict:
    paths = cfg["paths"]
    temp_root = Path(paths["temp_dir"])
    output_dir = Path(paths["output_dir"])
    output_format = cfg["output"]["format"]

    ensure_dir(temp_root)
    ensure_dir(output_dir)

    name = file_path.stem
    temp_folder = temp_root / name

    clean_dir(temp_folder)
    ensure_dir(temp_folder)

    try:
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            stats = extract_pdf_images(file_path, temp_folder, cfg)
        elif ext == ".docx":
            stats = extract_docx_images(file_path, temp_folder, cfg)
        elif ext == ".pptx":
            stats = extract_pptx_images(file_path, temp_folder, cfg)
        elif ext == ".xlsx":
            stats = extract_xlsx_images(file_path, temp_folder, cfg)
        else: 
            return {"skipped": True, "reason": f"extencion no soportada ({ext})"}
        
        if stats["saved"] > 0:
            if output_format == "zip":
                zip_path = output_dir / f"{name}.zip"
                create_zip_from_folder(temp_folder, zip_path)

            elif output_format == "folder":
                folder_path = output_dir / name
                copy_folder(temp_folder, folder_path)

            else:
                return {"error": f"formato de salida no soportado: {output_format}"}

        return stats
    except Exception as e:
        return {"error": str(e)}
    finally:
        clean_dir(temp_folder)

def list_input_files(input_path: Path, recursive: bool = False) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() in SUPPORTED_EXTS:
            return [input_path]
        return []

    if not input_path.is_dir():
        return []

    pattern = "**/*" if recursive else "*"

    files = [
        f for f in input_path.glob(pattern)
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ]

    return sorted(files)
