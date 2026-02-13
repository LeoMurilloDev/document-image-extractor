from pathlib import Path
from typing import Any, Dict, Set
import fitz
from ..utils.hashing import md5_bytes
from ..utils.files import is_small_kb
from ..utils.images import get_image_size, fails_dimension_filter, normalize_ext

def extract_pdf_images(pdf_path: Path, temp_folder: Path, cfg: Dict[str, Any]) -> Dict[str, int]:
    # Extraer las imagenes de vienen en el documento pdf
    filters = cfg["filters"]
    min_kb = filters["min_kb"]
    min_w = filters["min_width"]
    min_h = filters["min_height"]
    dedup_enabled = cfg["dedup"]["enabled"]

    stats = {"found": 0,"saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}

    hashes: Set[str] = set()
    counter = 0

    with fitz.open(str(pdf_path)) as pdf:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            for img in page.get_images(full=True):
                out_path = None
                try:
                    xref = img[0]
                    base = pdf.extract_image(xref)
                    data = base.get("image", b"")
                    ext = normalize_ext(base.get("ext", "bin"))

                    stats["found"] += 1

                    digest = md5_bytes(data)
                    if dedup_enabled and digest in hashes:
                        stats["duplicates"] += 1
                        continue

                    counter += 1
                    out_path = temp_folder / f"image_{counter:03d}_p{page_index+1:03d}.{ext}"
                    out_path.write_bytes(data)

                    # Filtro KB
                    if is_small_kb(out_path, min_kb):
                        stats["filtered_small"] += 1
                        out_path.unlink(missing_ok=True)
                        continue

                    # Filtro de dimenciones
                    dims = get_image_size(out_path)
                    if fails_dimension_filter(dims, min_w, min_h):
                        stats["filtered_dims"] += 1
                        out_path.unlink(missing_ok=True)
                        continue

                    if dedup_enabled:
                        hashes.add(digest)
                    
                    stats["saved"] += 1

                except Exception:
                    stats["errors"] += 1
                    if out_path is not None:
                        try:
                            out_path.unlink(missing_ok=True)
                        except Exception:
                            pass
    return stats