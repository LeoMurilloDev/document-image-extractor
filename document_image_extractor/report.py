import logging
from typing import Dict
logger = logging.getLogger("document_image_extractor")


def log_file_report(filename: str, stats: Dict) -> None:
    if stats.get("skipped"):
        logger.warning("%s: %s", filename, stats.get("reason"))
        return
    
    if "error" in stats:
        logger.error("%s: %s", filename, stats["error"])
        return
    
    if stats.get("saved", 0) > 0:
        logger.info(
            "%s | found=%s, saved=%s, dupes=%s, filtered_small=%s, filtered_dims=%s, errors=%s",
            filename,
            stats.get("found", 0),
            stats.get("saved", 0),
            stats.get("duplicates", 0),
            stats.get("filtered_small", 0),
            stats.get("filtered_dims", 0),
            stats.get("errors", 0),
        )
    else:
        logger.warning(
            "%s | No hay imágenes válidas | found=%s, dupes=%s, filtered_small=%s, filtered_dims=%s, errors=%s",
            filename,
            stats.get("found", 0),
            stats.get("duplicates", 0),
            stats.get("filtered_small", 0),
            stats.get("filtered_dims", 0),
            stats.get("errors", 0),
        )

def accumulate_totals(total: Dict[str, int], stats: Dict) -> None:
    for k in total:
        total[k] += int(stats.get(k, 0))

def log_summary(files: int, skipped: int, failed: int, total: Dict[str, int]) -> None:
    logger.info("=== RESUMEN ===")
    logger.info(
        "files=%s, skipped=%s, failed=%s | found=%s, saved=%s, dupes=%s, filtered_small=%s, filtered_dims=%s, errors=%s",
        files, skipped, failed,
        total.get("found", 0),
        total.get("saved", 0),
        total.get("duplicates", 0),
        total.get("filtered_small", 0),
        total.get("filtered_dims", 0),
        total.get("errors", 0),
    )