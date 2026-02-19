import logging
from pathlib import Path
from typing import Any, Dict

def setup_logging(cfg: Dict[str, Any]) -> None:
    log_cfg = cfg.get("logging", {}) if isinstance(cfg, dict) else {}

    level_name = str(log_cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = str(log_cfg.get("format", "%(asctime)s | %(levelname)s | %(message)s"))
    datefmt = str(log_cfg.get("datefmt", "%Y-%m-%d %H:%M:%S"))

    log_file = str(log_cfg.get("log_file", "logs/run.log")).strip() or "logs/run.log"
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handlers = [logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8")]

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, handlers=handlers, force=True)