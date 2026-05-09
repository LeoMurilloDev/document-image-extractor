import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, Set, Tuple
from ..utils.hashing import md5_bytes
from ..utils.files import is_small_kb
from ..utils.images import get_image_size, fails_dimension_filter, normalize_ext

IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif", "webp", "emf", "wmf", "svg"}

def extract_ooxml_media_images(archive_path: Path, media_prefixes: Tuple[str, ...], temp_folder: Path, cfg: Dict[str, Any], source_tag: str) -> Dict[str, int]:
    # Extraer imagenes desde un OOXML (pptx, xlsx) leyendo lor archivos en media/

    filters = cfg["filters"]
    min_kb = int(filters["min_kb"])
    min_w = int(filters["min_width"])
    min_h = int(filters["min_height"])
    dedup_enabled = bool(cfg["dedup"]["enabled"])

    stats: Dict[str, int] = {"found": 0, "saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}
    hashes: Set[str] = set()
    counter = 0

    with zipfile.ZipFile(archive_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename

            if name.endswith("/"): continue
            if not any(name.startswith(prefix) for prefix in media_prefixes): continue
            ext = normalize_ext(Path(name).suffix.replace(".",""))
            if not ext or ext not in IMAGE_EXTS: continue

            out_path = None
            try:
                data = zf.read(name)
                stats["found"] += 1

                digest = md5_bytes(data)
                if dedup_enabled and digest in hashes:
                    stats["duplicates"] += 1
                    continue

                counter += 1
                out_path = temp_folder / f"image_{counter:03d}_{source_tag}.{ext}"
                out_path.write_bytes(data)

                if is_small_kb(out_path, min_kb):
                    stats["filtered_small"] += 1
                    out_path.unlink(missing_ok=True)
                    continue

                dims = get_image_size(out_path)
                if fails_dimension_filter(dims, min_w, min_h):
                    stats["filtered_dims"] += 1
                    out_path.unlink(missing_ok=True)
                    continue

                if dedup_enabled: hashes.add(digest)

                stats["saved"] += 1
            except Exception:
                stats["errors"] += 1
                if out_path is not None:
                    try:
                        out_path.unlink(missing_ok=True)
                    except Exception:
                        pass
    return stats