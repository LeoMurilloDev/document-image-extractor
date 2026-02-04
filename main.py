# Librerias Necesarias para Direcciones de archivos y creacion de Zip
import os
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from docx import Document # Libreria para manejo de documentos Word
import fitz # Libreria para manejo de documentos PDF
from PIL import Image

# Configuracion Defautl en caso de no encontrar config.json
DEFAULT_CONFIG = {
    "paths": {
        "input_dir": "Entradas_archivos",
        "output_dir": "Salidas_archivos",
        "temp_dir": "temp"
    },
    "filters": {
        "min_kb": 5, # Tamaño minimo de las imagenes
        "min_width": 0, # 0 = deshabilitado
        "min_height": 0 # 0 = deshabilitado
    },
    "dedup": {"enabled": True},
    "output": {"format": "zip"}
}

# Utilidades
def cargar_config(config_path: Path = Path("config.json")) -> dict:
    # Cargar la configuracion de archivo config.json, en caso de que falten propiedades de convinara con DEFAUTL_CONFIG
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if not config_path.exists():
        return config
    try:
        user_cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        # En caso de no poder abrir la configuracion o que tenga errores regresamos configuracion default 
        return config
    
    for section in ("paths", "filters", "dedup", "output"):
        if isinstance(user_cfg.get(section), dict):
            config[section].update(user_cfg[section])
    
    config["filters"]["min_kb"] = int(config["filters"].get("min_kb", 5))
    config["filters"]["min_width"] = int(config["filters"].get("min_width", 0))
    config["filters"]["min_height"] = int(config["filters"].get("min_height", 0))
    config["dedup"]["enabled"] = bool(config["dedup"].get("enabled", True))
    config["output"]["format"] = str(config["output"].get("format", "zip")).lower()

    return config


def calcular_md5(data: bytes) -> str:
    # Calcular el hash MD5 de los datos proporcionados
    return hashlib.md5(data).hexdigest()

def crear_zip(carpeta_origen: Path, zip_destino: Path) -> None:
    # Crear un zip con el contenido de carpeta_origen
    with zipfile.ZipFile(zip_destino, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for archivo in carpeta_origen.rglob('*'):
            if archivo.is_file(): 
                zf.write(archivo, arcname=archivo.relative_to(carpeta_origen))

def limpiar_carpeta(carpeta: Path) -> None:
    # EliminarArchivos de la carpeta especificada
    if carpeta.exists(): 
        shutil.rmtree(carpeta, ignore_errors=True)

def normalizar_extension(ext: str)-> str:
    # Normalizacion de extenciones para imagenes
    ext = (ext or "bin").lower().strip(".")
    if ext in ("jpeg", "jpe"):
        return "jpg"
    if ext == "tif":
        return "tiff"
    return ext

def obtener_dimensiones(path: Path) -> tuple[int, int] | None:
    # Devolver width, height o None si no se puede leer 
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None

def es_muy_pequena_por_kb(path: Path, min_kb: int) -> bool:
    return (path.stat().st_size / 1024) < min_kb

def falla_por_dimensiones(dim: tuple[int, int] | None, min_w: int, min_h: int) -> bool:
    if min_w <= 0 and min_h <= 0:
        return False
    if dim is None:
        return False
    w, h = dim
    if min_w > 0 and w < min_w:
        return True
    if min_h > 0 and h < min_h:
        return True
    return False


def obtener_extension_docx(image_part) -> str: 
    # Deduccion de la extencion de la imagenes en documentos .docx
    ct = getattr(image_part, "content_type", None)
    if ct and "/" in ct:
        return normalizar_extension(ct.split("/")[-1])
    partname = str(getattr(image_part, "partname", "")).lower()
    if "." in partname:
        return normalizar_extension(partname.split(".")[-1])
    return "bin"


# Extractores
def extraer_imagenes_word(docx_path: Path, carpeta_temp_archivo: Path, cfg: dict) -> dict:
    # Extraer las imagenes que vienen en el documento docx
    filters = cfg["filters"]
    min_kb = filters["min_kb"]
    min_w = filters["min_width"]
    min_h = filters["min_height"]
    dedup_enabled = cfg["dedup"]["enabled"]

    stats = {"found": 0,"saved": 0,"duplicates": 0,"filtered_small": 0,"filtered_dims": 0,"errors": 0,}

    doc = Document(str(docx_path))
    image_parts = list(doc.part.package.image_parts)
    stats["found"] = len(image_parts)
    hashes = set()

    for i, image_part in enumerate(image_parts, start=1):
        try:
            blob = image_part.blob
            md5 = calcular_md5(blob)

            if dedup_enabled and md5 in hashes:
                stats["duplicates"] += 1
                continue

            ext = obtener_extension_docx(image_part)
            nombre = f"image_{i:03d}.{ext}"
            ruta_salida = carpeta_temp_archivo / nombre
            ruta_salida.write_bytes(blob)

            if es_muy_pequena_por_kb(ruta_salida, min_kb):
                stats["filtered_small"] += 1
                ruta_salida.unlink(missing_ok=True)
                continue

            dims = obtener_dimensiones(ruta_salida)
            if falla_por_dimensiones(dims, min_w, min_h):
                stats["filtered_dims"] += 1
                ruta_salida.unlink(missing_ok=True)
                continue

            if dedup_enabled:
                hashes.add(md5)

            stats["saved"] += 1

        except Exception:
            stats["errors"] += 1
            try:
                if "ruta_salida" in locals() and isinstance(ruta_salida, Path):
                    ruta_salida.unlink(missing_ok=True)
            except Exception:
                pass

    return stats

def extraer_imagenes_pdf(pdf_path: Path, carpeta_temp_archivo: Path, cfg: dict) -> dict:
    # Extraer las imagenes que vienen en el documento pdf
    filters = cfg["filters"]
    min_kb = filters["min_kb"]
    min_w = filters["min_width"]
    min_h = filters["min_height"]
    dedup_enabled = cfg["dedup"]["enabled"]

    stats = {"found": 0,"saved": 0, "duplicates": 0, "filtered_small": 0, "filtered_dims": 0, "errors": 0}

    hashes = set()
    contador = 0

    with fitz.open(str(pdf_path)) as pdf:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            for img in page.get_images(full=True):
                try:
                    xref = img[0]
                    base_image = pdf.extract_image(xref)

                    image_bytes = base_image.get("image", b"")
                    ext = normalizar_extension(base_image.get("ext", "bin"))

                    stats["found"] += 1

                    md5 = calcular_md5(image_bytes)
                    if dedup_enabled and md5 in hashes:
                        stats["duplicates"] += 1
                        continue

                    contador += 1
                    nombre = f"image_{contador:03d}_p{page_index+1:03d}.{ext}"
                    ruta_salida = carpeta_temp_archivo / nombre
                    ruta_salida.write_bytes(image_bytes)

                    if es_muy_pequena_por_kb(ruta_salida, min_kb):
                        stats["filtered_small"] += 1
                        ruta_salida.unlink(missing_ok=True)
                        continue

                    dims = obtener_dimensiones(ruta_salida)
                    if falla_por_dimensiones(dims, min_w, min_h):
                        stats["filtered_dims"] += 1
                        ruta_salida.unlink(missing_ok=True)
                        continue

                    if dedup_enabled:
                        hashes.add(md5)

                    stats["saved"] += 1

                except Exception:
                    stats["errors"] += 1
                    try:
                        if "ruta_salida" in locals() and isinstance(ruta_salida, Path):
                            ruta_salida.unlink(missing_ok=True)
                    except Exception:
                        pass
    return stats

def procesar_archivo(ruta_archivo: Path, cfg: dict, paths: dict) -> dict:
    # Procesa un archivo infiviual donde se valida la extencion del archivo para su debido proceso interno
    temp_dir = Path(paths["temp_dir"])
    output_dir = Path(paths["output_dir"])
    output_format = cfg["output"]["format"]
    nombre_base = ruta_archivo.stem
    carpeta_temp_archivo = temp_dir / nombre_base

    # Se limpia la carpeta en caso de una version de la carpeta previa
    limpiar_carpeta(carpeta_temp_archivo)
    carpeta_temp_archivo.mkdir(parents=True, exist_ok=True)

    # Validacion de la extencion del archivo
    try:
        ext = ruta_archivo.suffix.lower()
        if ext == '.pdf':
            stats = extraer_imagenes_pdf(ruta_archivo, carpeta_temp_archivo, cfg)
        elif ext == '.docx':
            stats = extraer_imagenes_word(ruta_archivo, carpeta_temp_archivo, cfg)
        else: 
            return {"skipped": True, "reason": f"extensión no soportada ({ext})"}
        
        if stats["saved"] > 0:
            if output_format == "zip":
                zip_path = output_dir / f"{nombre_base}.zip"
                crear_zip(carpeta_temp_archivo, zip_path)

        return stats

    except Exception as e: 
        return {"error": str(e)}
    finally: 
        limpiar_carpeta(carpeta_temp_archivo)

def print_reporte(nombre: str, stats: dict) -> None:
    if stats.get("skipped"):
        print(f"⚠ {nombre}: {stats.get('reason')}")
        return

    if "error" in stats:
        print(f"❌ {nombre}: {stats['error']}")
        return

    if stats.get("saved", 0) > 0:
        print(
            f"✔️ {nombre}: "
            f"found={stats['found']}, saved={stats['saved']}, "
            f"dupes={stats['duplicates']}, "
            f"filtered_small={stats['filtered_small']}, "
            f"filtered_dims={stats['filtered_dims']}, "
            f"errors={stats['errors']}"
        )
    else:
        print(
            f"⚠️ {nombre}: No hay imágenes válidas | "
            f"found={stats['found']}, dupes={stats['duplicates']}, "
            f"filtered_small={stats['filtered_small']}, "
            f"filtered_dims={stats['filtered_dims']}, "
            f"errors={stats['errors']}"
        )


def main(): 
    # Verificacion de que las carpetas definidas en la ruta existan y configuraciones definidas
    cfg = cargar_config()
    paths = cfg["paths"]
    input_dir = Path(paths["input_dir"])
    output_dir = Path(paths["output_dir"])
    temp_dir = Path(paths["temp_dir"])
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    #Listado de documentos inicializacion
    archivos = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in (".pdf", ".docx")
    ]

    if not archivos:
        print(f"⚠ No se encontraron archivos .pdf o .docx en: {input_dir.resolve()}")
        return
    
    total = {"found": 0, "saved": 0, "duplicates": 0,"filtered_small": 0, "filtered_dims": 0, "errors": 0}
    skipped = 0
    failed = 0
    
    for archivo in archivos:
        stats = procesar_archivo(archivo, cfg, paths)
        print_reporte(archivo.name, stats)
        if stats.get("skipped"):
            skipped += 1
            continue
        if "error" in stats:
            failed += 1
            continue
        for k in total:
            total[k] += stats.get(k, 0)

    print("\n=== RESUMEN ===")
    print(
        f"files={len(archivos)}, skipped={skipped}, failed={failed} | "
        f"found={total['found']}, saved={total['saved']}, dupes={total['duplicates']}, "
        f"filtered_small={total['filtered_small']}, filtered_dims={total['filtered_dims']}, "
        f"errors={total['errors']}"
    )

if __name__ == "__main__":
    main()
