import json 
import subprocess
import sys
from pathlib import Path
from .conftest import create_fake_pptx

def test_cli_help_runs_successfully():
    repo_root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--input" in result.stdout
    assert "--recursive" in result.stdout
    assert "--min-kb" in result.stdout

def test_cli_format_folder(tmp_path: Path, sample_images):
    repo_root = Path(__file__).resolve().parents[1]

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    temp_dir = tmp_path / "temp"
    logs_dir = tmp_path / "logs"

    input_dir.mkdir()

    pptx_path = input_dir / "folder_mode.pptx"
    create_fake_pptx(
        pptx_path,
        {
            # Usamos JPG para asegurar que pase filtros por tamaño
            "photo.jpg": sample_images["photo_jpg"].read_bytes(),
        },
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "paths": {
                    "input_dir": str(input_dir),
                    "output_dir": str(output_dir),
                    "temp_dir": str(temp_dir),
                },
                "filters": {
                    "min_kb": 1,
                    "min_width": 0,
                    "min_height": 0,
                },
                "logging": {
                    "level": "INFO",
                    "log_file": str(logs_dir / "run.log"),
                },
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--config",
            str(config_path),
            "--input",
            str(pptx_path),
            "--output",
            str(output_dir),
            "--temp-dir",
            str(temp_dir),
            "--format",
            "folder",
            "--min-kb",
            "1",
            "--log-file",
            str(logs_dir / "run.log"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    output_folder = output_dir / "folder_mode"
    assert output_folder.exists()
    assert output_folder.is_dir()

    extracted_files = list(output_folder.iterdir())
    assert len(extracted_files) == 1

    assert (logs_dir / "run.log").exists()