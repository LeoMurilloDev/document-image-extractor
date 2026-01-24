import os
import shutil
from docx import Document
import fitz  # PyMuPDF
from PIL import Image
import zipfile
import hashlib



CARPETA_ENTRADA = "Entradas_archivos"
CARPETA_SALIDAS = "Salidas_archivos"
CARPETA_TEM = "temp"

def crear_carpetas():
    """Crear la carpeta necesaria si no existe"""
    os.makedirs(CARPETA_ENTRADA, exist_ok=True)
    os.makedirs(CARPETA_SALIDAS, exist_ok=True)
    os.makedirs(CARPETA_TEM, exist_ok=True)

def calcular_hash_imagen(ruta_imagen):
    """Calcular el hash de una imagen"""
    with open(ruta_imagen, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def es_imagen_valida(ruta_imagen, min_kb=5, hashes_existentes=None):
    """Verificar si una imagen es válida (no vacía y no muy pequeña)"""
    if hashes_existentes is None:
        hashes_existentes = set()

    tamano = os.path.getsize(ruta_imagen) / 1024
    if tamano < min_kb:
        return False
    
    imagen_hash = calcular_hash_imagen(ruta_imagen)
    if imagen_hash in hashes_existentes:
        return False
    
    hashes_existentes.add(imagen_hash)
    return True



def extraer_imagenes_word(archivo_docx, carpeta_destino):
    """Extraer imagenes de un archivo word (.docx)"""
    doc = Document(archivo_docx)
    hashes_existentes = set()
    contador = 0
    for i, rel in  enumerate(doc.part.rels.values()):
        if "image" in rel.target_ref:
            img_data = rel.target_part.blob
            ruta_temp = os.path.join(carpeta_destino, f"temp_{i}.png")
            
            with open(ruta_temp, "wb") as f:
                f.write(img_data)
            
            if es_imagen_valida(ruta_temp, min_kb=5, hashes_existentes=hashes_existentes):
                ruta_final = os.path.join(carpeta_destino, f"imagen_{contador}.png")
                os.rename(ruta_temp, ruta_final)
                contador += 1
            else:
                os.remove(ruta_temp)

def extraer_imagenes_pdf(archivo_pdf, carpeta_destino):
    """Extraer imagenes de un archivo pdf (.pdf)"""
    pdf = fitz.open(archivo_pdf)
    hashes_existentes = set()
    contador = 0

    for i, pagina in enumerate(pdf):
        for j, img in enumerate(pagina.get_images()):
            xref = img[0]
            base_img = pdf.extract_image(xref)
            img_data = base_img["image"]
            extension = base_img["ext"]
            ruta_temp = os.path.join(carpeta_destino, f"temp_pdf_{i}_{j}.{extension}")
            
            with open(ruta_temp, "wb") as f:
                f.write(img_data)
            
            if es_imagen_valida(ruta_temp, min_kb=5, hashes_existentes=hashes_existentes):
                ruta_final = os.path.join(carpeta_destino, f"imagen_pdf_{contador}.{extension}")
                os.rename(ruta_temp, ruta_final)
                contador += 1
            else:
                os.remove(ruta_temp)

def crear_rar(carpeta_imagenes, nombre_archivo):
    """Crear un archivo rar con las imagenes de la carpeta"""
    nombre_zip = os.path.join(CARPETA_SALIDAS, f"{nombre_archivo}.zip")
    with zipfile.ZipFile(nombre_zip, "w") as zf:
        for img in os.listdir(carpeta_imagenes):
            img_path = os.path.join(carpeta_imagenes, img)
            zf.write(img_path, img)

def procesar_archivos():
    """Procesar los archivos de la carpeta de entrada"""
    for archivo in os.listdir(CARPETA_ENTRADA):
        nombre, extencion = os.path.splitext(archivo)
        carpeta_temp = os.path.join(CARPETA_TEM, nombre)
        os.makedirs(carpeta_temp, exist_ok=True)

        archivo_completo = os.path.join(CARPETA_ENTRADA, archivo)

        try:
            if extencion.lower() == ".docx":
                extraer_imagenes_word(archivo_completo, carpeta_temp)
            elif extencion.lower() == ".pdf":
                extraer_imagenes_pdf(archivo_completo, carpeta_temp)

            if os.listdir(carpeta_temp):
                crear_rar(carpeta_temp, nombre)
                print(f"✔ {archivo}: Imágenes extraídas y comprimidas.")
            else:
                print(f"⚠ {archivo}: No contiene imágenes.")

            shutil.rmtree(carpeta_temp)
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")

if __name__ == "__main__":
    crear_carpetas()
    procesar_archivos()
    print("✅ Proceso completado.")