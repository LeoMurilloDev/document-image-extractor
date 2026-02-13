import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "paths": {
        "input_dir": "Entradas_archivos",
        "output_dir": "Salidas_archivos",
        "temp_dir": "temp",
    },
    "filters": {
        "min_kb": 5,
        "min_width": 0,
        "min_height": 0,
    },
    "dedup": {"enabled": True},
    "output": {"format": "zip"},
}

# Cargar la configuracion del programa y parametros basicos
def load_config(config_path: Path = Path("config.json")) -> Dict[str, Any]:
    # Carga de archivo config.json y en caso de configuraciones faltantes he hace mescla con DEFAULT_CONFIG
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if not config_path.exists(): return cfg

    try:
        user_cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return cfg
    
    for section in ("paths", "filters", "dedup", "output"):
        if isinstance(user_cfg.get(section), dict): cfg[section].update(user_cfg[section])
    
    # Normalizacion minima
    cfg["filters"]["min_kb"] = int(cfg["filters"].get("min_kb", 5))
    cfg["filters"]["min_width"] = int(cfg["filters"].get("min_width", 0))
    cfg["filters"]["min_height"] = int(cfg["filters"].get("min_height", 0))
    cfg["dedup"]["enabled"] = bool(cfg["dedup"].get("enabled", True))
    cfg["output"]["format"] = str(cfg["output"].get("format", "zip")).lower()

    return cfg
