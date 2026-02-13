from pathlib import Path
from typing import Optional, Tuple
from PIL import Image


def get_image_size(path: Path) -> Optional[Tuple[int, int]]:
    # Devolver el ancho y el alto de las imagenes, En caso de no poder abrir regresa None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None

def fails_dimension_filter(dims: Optional[Tuple[int, int]], min_w: int, min_h: int) -> bool:
    # En caso de que dims sea None se omiten validaciones
    if min_w <= 0 and min_h <= 0: return False
    if dims is None: return False

    w, h = dims
    if min_w > 0 and w < min_w: return True
    if min_h > 0 and h < min_h: return True

    return False

def normalize_ext(ext: str) -> str:
    # Normalizacion de extenciones para imagenes
    ext = (ext or "bin").lower().strip(".")
    if ext in ("jpeg", "jpe"):
        return "jpg"
    if ext == "tif":
        return "tiff"
    return ext