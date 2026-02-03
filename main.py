# Librerias Necesarias para Direcciones de archivos y creacion de Zip
import os
import shutil
import zipfile
import hashlib
from pathlib import Path
from docx import Document # Libreria para manejo de documentos Word
import fitz # Libreria para manejo de documentos PDF


# Configuracion De Carpetas de Entrada y Salida de los documentos Ademas de configuracion de parametros adicionales
CARPETA_ENTRADA = Path("Entradas_archivos")
CARPETA_SALIDAS = Path("Salidas_archivos")
CARPETA_TEMP = Path("temp")
MIN_KB_DEFAULT = 5

def crear_carpetas():
    # Creacion de carpetas en caso de que estas no existan
    os.makedirs(CARPETA_ENTRADA, exist_ok=True)
    os.makedirs(CARPETA_SALIDAS, exist_ok=True)
    os.makedirs(CARPETA_TEMP, exist_ok=True)

def calcular_md5(data: bytes) -> str:
    # Calcular el hash MD5 de los datos proporcionados
    return hashlib.md5(data).hexdigest()

def es_muy_pequena(ruta: Path, min_kb: int) -> bool:
    # Verifica si el archivo en la ruta dada es menor que el tamaño minimo en KB
    return (ruta.stat().st_size / 1024) < min_kb

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
    ext = ext.lower().strip(".")
    if ext in ("jpeg", "jpe"):
        return "jpg"
    if ext == "tif":
        return "tiff"
    return ext

def obtener_extension_docx(image_part) -> str: 
    # Deduccion de la extencion de la imagenes en documentos .docx
    ct = getattr(image_part, "content_type", None)
    if ct and "/" in ct:
        guessed = ct.split("/")[-1]
        guessed = normalizar_extension(guessed)
        return guessed
    
    partname = str(getattr(image_part, "partname", "")).lower()
    if "." in partname:
        guessed = partname.split(".")[-1]
        guessed = normalizar_extension(guessed)
        return guessed
    return "bin"


# Extractores
def extraer_imagenes_word(docx_path: Path, carpeta_temp_archivo: Path, min_kb:int) -> dict:
    # Extraer las imagenes que vienen en el documento docx
    stats = {"encontradas": 0, "guardadas": 0, "duplicadas": 0, "pequenas": 0}
    doc = Document(str(docx_path))
    hashes = set()

    image_parts = list(doc.part.package.image_parts)
    stats["encontradas"] = len(image_parts)

    for i, image_part in enumerate(image_parts, start=1):
        blob = image_part.blob
        md5 = calcular_md5(blob)
        if md5 in hashes:
            stats["duplicadas"] += 1
            continue
        ext = obtener_extension_docx(image_part)
        nombre = f"image_{i:03d}.{ext}"
        ruta_salida = carpeta_temp_archivo / nombre
        ruta_salida.write_bytes(blob)

        if es_muy_pequena(ruta_salida, min_kb):
            stats["pequenas"] += 1
            ruta_salida.unlink(missing_ok=True)
            continue
        hashes.add(md5)
        stats["guardadas"] += 1
    return stats

def extraer_imagenes_pdf(pdf_path: Path, carpeta_temp_archivo: Path, min_kb: int) -> dict:
    # Extraer las imagenes que vienen en el documento pdf
    stats = {"encontradas": 0, "guardadas": 0, "duplicadas": 0, "pequenas": 0}
    hashes = set()
    contador = 0

    with fitz.open(str(pdf_path)) as pdf:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image.get("image", b"")
                ext = normalizar_extension(base_image.get("ext", "bin"))

                stats['encontradas'] += 1

                md5 = calcular_md5(image_bytes)
                if md5 in hashes:
                    stats["duplicadas"] += 1
                    continue

                contador += 1
                nombre = f"image_{contador:03d}_p{page_index+1:03d}.{ext}"
                ruta_salida = carpeta_temp_archivo / nombre
                ruta_salida.write_bytes(image_bytes)

                if es_muy_pequena(ruta_salida, min_kb):
                    stats["pequenas"] += 1
                    ruta_salida.unlink(missing_ok=True)
                    continue

                hashes.add(md5)
                stats['guardadas'] += 1
    return stats

def procesar_archivo(ruta_archivo: Path, min_kb: int = MIN_KB_DEFAULT) -> None:
    # Procesa un archivo infiviual donde se valida la extencion del archivo para su debido proceso interno
    nombre_base = ruta_archivo.stem
    carpeta_temp_archivo = CARPETA_TEMP / nombre_base

    # Se limpia la carpeta en caso de una version de la carpeta previa
    limpiar_carpeta(carpeta_temp_archivo)
    carpeta_temp_archivo.mkdir(parents=True, exist_ok=True)


    # Validacion de la extencion del archivo
    try:
        ext = ruta_archivo.suffix.lower()
        if ext == '.pdf':
            stats = extraer_imagenes_pdf(ruta_archivo, carpeta_temp_archivo, min_kb)
        elif ext == '.docx':
            stats = extraer_imagenes_word(ruta_archivo, carpeta_temp_archivo, min_kb)
        else: 
            print(f"WARNING {ruta_archivo.name}: Extencion no soportada ({ext})")
            return
        
        if stats["guardadas"] > 0:
            zip_path = CARPETA_SALIDAS / f"{nombre_base}.zip"
            crear_zip(carpeta_temp_archivo,zip_path)
            print(
                f"SUCCESS {ruta_archivo.name}: guardadas = {stats['guardadas']}, "
                f"Duplicadas = {stats['duplicadas']}, "
                f"Pequeñas = {stats['pequenas']}, "
                f"Encontradas = {stats['encontradas']} ")
        else: 
            print(
                f"WARNING  {ruta_archivo.name}: No hay imagenes validas, "
                f"(encontradas = {stats['encontradas']}, duplicadas = {stats['duplicadas']}, pequeñas = {stats['pequenas']})")
    except Exception as e: 
        print(f"ERROR Error procesando la ruta {ruta_archivo.name}: {e}")
    finally: 
        limpiar_carpeta(carpeta_temp_archivo)


def main(): 
    # Verificacion de que las carpetas definidas en la ruta existan
    crear_carpetas()

    #Listado de documentos inicializacion
    archivos = []

    if CARPETA_ENTRADA.exists():
        for f in CARPETA_ENTRADA.iterdir():
            if f.is_file() and f.suffix.lower() in (".pdf", ".docx"):
                archivos.append(f)
    
    if not archivos:
        print(f"WARNING: No se encontraron archivos .pdf o .docx en {CARPETA_ENTRADA.resolve()}")
        return
    
    for archivo in archivos:
        procesar_archivo(archivo, min_kb=MIN_KB_DEFAULT)

if __name__ == "__main__":
    main()
