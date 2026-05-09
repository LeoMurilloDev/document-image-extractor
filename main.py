import logging
from pathlib import Path
from document_image_extractor.cli import parse_args, apply_cli_overrides
from document_image_extractor.config import load_config
from document_image_extractor.logging_setup import setup_logging
from document_image_extractor.pipeline import list_input_files, process_file, SUPPORTED_EXTS
from document_image_extractor.report import log_file_report, accumulate_totals, log_summary
from document_image_extractor.utils.files import ensure_dir

logger = logging.getLogger("document_image_extractor")

def main():
    args = parse_args()

    cfg = load_config(Path(args.config_path))
    cfg = apply_cli_overrides(cfg, args)
    setup_logging(cfg)
    paths = cfg["paths"]
    runtime = cfg["runtime"]

    input_path = Path(runtime["input_path"])
    output_dir = Path(paths["output_dir"])
    temp_dir = Path(paths["temp_dir"])
    recursive = bool(runtime["recursive"])

    if not input_path.exists():
        if runtime.get("input_was_provided"):
            logger.error("La ruta de entrada no existe: %s", input_path)
            return
        ensure_dir(input_path)

    ensure_dir(output_dir)
    ensure_dir(temp_dir)

    logger.debug("Input path: %s", input_path.resolve())
    logger.debug("Output dir: %s", output_dir.resolve())
    logger.debug("Temp dir: %s", temp_dir.resolve())
    logger.debug("Recursive: %s", recursive)
    logger.debug("Supported extensions: %s", ", ".join(sorted(SUPPORTED_EXTS)))
    logger.debug(
        "Filters: min_kb=%s, min_width=%s, min_height=%s",
        cfg["filters"]["min_kb"],
        cfg["filters"]["min_width"],
        cfg["filters"]["min_height"],
    )
    logger.debug("Output format: %s", cfg["output"]["format"])
    logger.debug("Dedup enabled: %s", cfg["dedup"]["enabled"])

    files = list_input_files(input_path, recursive=recursive)

    if not files:
        logger.warning(
            "No se encontraron archivos soportados (%s) en: %s",
            ", ".join(sorted(SUPPORTED_EXTS)),
            input_path.resolve(),
        )
        return
    
    total = {"found": 0, "saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}
    skipped = 0
    failed = 0

    for f in files:
        stats = process_file(f, cfg)
        log_file_report(f.name, stats)

        if stats.get("skipped"):
            skipped += 1
            continue

        if "error" in stats:
            failed += 1
            continue

        accumulate_totals(total, stats)
    
    log_summary(files=len(files), skipped=skipped, failed=failed, total=total)

if __name__== "__main__":
    main()