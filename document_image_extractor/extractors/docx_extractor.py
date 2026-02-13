from pathlib import Path
from typing import Any, Dict, Set
from docx import Document
from ..utils.hashing import md5_bytes
from ..utils.files import is_small_kb
from ..utils.images import get_image_size, fails_dimension_filter, normalize_ext


def _docx_image_ext(image_part) -> str:
    ct = getattr(image_part, "content_type", None)
    if ct and "/" in ct:
        return normalize_ext(ct.split("/")[-1])

    partname = str(getattr(image_part, "partname", "")).lower()
    if "." in partname:
        return normalize_ext(partname.split(".")[-1])

    return "bin"


def extract_docx_images(docx_path: Path, temp_folder: Path, cfg: Dict[str, Any]) -> Dict[str, int]:
    filters = cfg["filters"]
    min_kb = int(filters["min_kb"])
    min_w = int(filters["min_width"])
    min_h = int(filters["min_height"])
    dedup_enabled = bool(cfg["dedup"]["enabled"])
    stats: Dict[str, int] = {"found": 0, "saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}

    doc = Document(str(docx_path))
    image_parts = list(doc.part.package.image_parts)
    stats["found"] = len(image_parts)
    hashes: Set[str] = set()

    for i, image_part in enumerate(image_parts, start=1):
        out_path = None
        try:
            blob = image_part.blob
            digest = md5_bytes(blob)

            if dedup_enabled and digest in hashes:
                stats["duplicates"] += 1
                continue

            ext = _docx_image_ext(image_part)
            out_path = temp_folder / f"image_{i:03d}.{ext}"
            out_path.write_bytes(blob)

            if is_small_kb(out_path, min_kb):
                stats["filtered_small"] += 1
                out_path.unlink(missing_ok=True)
                continue

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