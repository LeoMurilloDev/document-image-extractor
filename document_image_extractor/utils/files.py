import shutil
import zipfile
from pathlib import Path

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def clean_dir(path: Path) -> None:
    # Eliminar archivos de la carpeta esfecifica
    if path.exists(): shutil.rmtree(path, ignore_errors=True)

def create_zip_from_folder(folder: Path, zip_destine: Path) -> None:
    # Crear un zip con el contenido de folder
    with zipfile.ZipFile(zip_destine, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in folder.rglob("*"):
            if file.is_file(): zf.write(file, arcname=file.relative_to(folder))

def is_small_kb(path: Path, min_kb: int) -> bool:
    # Validacion booleana si la imagen es mas chica que el parametro min_kb configurado
    return (path.stat().st_size / 1024) < min_kb