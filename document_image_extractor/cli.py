import argparse
from typing import Any, Dict
from . import __version__

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="document-image-extractor",
        description=(
            "Extract embedded images from PDF, DOCX, PPTX and XLSX files. "
            "Supports deduplication, filters and ZIP/folder output."
        ),
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        default="config.json",
        help="Ruta del archivo de configuración. Default: config.json",
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="input_path",
        default=None,
        help="Archivo o carpeta de entrada. Default: paths.input_dir del config.",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        default=None,
        help="Carpeta de salida. Default: paths.output_dir del config.",
    )

    parser.add_argument(
        "--temp-dir",
        dest="temp_dir",
        default=None,
        help="Carpeta temporal. Default: paths.temp_dir del config.",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Procesa archivos dentro de subcarpetas cuando --input es una carpeta.",
    )

    parser.add_argument(
        "--min-kb",
        dest="min_kb",
        type=int,
        default=None,
        help="Tamaño mínimo en KB para guardar una imagen.",
    )

    parser.add_argument(
        "--min-width",
        dest="min_width",
        type=int,
        default=None,
        help="Ancho mínimo en pixeles. 0 desactiva el filtro.",
    )

    parser.add_argument(
        "--min-height",
        dest="min_height",
        type=int,
        default=None,
        help="Alto mínimo en pixeles. 0 desactiva el filtro.",
    )

    dedup_group = parser.add_mutually_exclusive_group()
    dedup_group.add_argument(
        "--dedup",
        dest="dedup_enabled",
        action="store_true",
        help="Activa deduplicación por hash.",
    )
    dedup_group.add_argument(
        "--no-dedup",
        dest="dedup_enabled",
        action="store_false",
        help="Desactiva deduplicación por hash.",
    )
    parser.set_defaults(dedup_enabled=None)

    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["zip", "folder"],
        default=None,
        help="Formato de salida. Opciones: zip, folder. Default: config output.format.",
    )

    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Nivel de logs.",
    )

    parser.add_argument(
        "--log-file",
        dest="log_file",
        default=None,
        help="Ruta del archivo de logs. Ejemplo: logs/run.log",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args()

def apply_cli_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    cfg.setdefault("runtime", {})

    # Input runtime: puede ser archivo o carpeta
    cfg["runtime"]["input_path"] = args.input_path or cfg["paths"]["input_dir"]
    cfg["runtime"]["input_was_provided"] = bool(args.input_path)
    cfg["runtime"]["recursive"] = bool(args.recursive)

    # Paths
    if args.output_dir is not None:
        cfg["paths"]["output_dir"] = args.output_dir

    if args.temp_dir is not None:
        cfg["paths"]["temp_dir"] = args.temp_dir

    # Filters
    if args.min_kb is not None:
        cfg["filters"]["min_kb"] = int(args.min_kb)

    if args.min_width is not None:
        cfg["filters"]["min_width"] = int(args.min_width)

    if args.min_height is not None:
        cfg["filters"]["min_height"] = int(args.min_height)

    # Dedup
    if args.dedup_enabled is not None:
        cfg["dedup"]["enabled"] = bool(args.dedup_enabled)

    # Output
    if args.output_format is not None:
        cfg["output"]["format"] = args.output_format

    # Logging
    if args.log_level is not None:
        cfg["logging"]["level"] = args.log_level

    if args.log_file is not None:
        cfg["logging"]["log_file"] = args.log_file

    return cfg