from pathlib import Path
from typing import Any, Dict
from .ooxml_media_extractor import extract_ooxml_media_images

def extract_xlsx_images(xlsx_path: Path, temp_folder: Path, cfg: Dict[str, Any]) -> Dict[str, int]:
    return extract_ooxml_media_images(
        archive_path=xlsx_path,
        media_prefixes=("xl/media/",),
        temp_folder=temp_folder,
        cfg=cfg,
        source_tag="xlsx",
    )