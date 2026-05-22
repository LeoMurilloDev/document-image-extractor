from pathlib import Path
from document_image_extractor.pipeline import list_input_files, process_file
from .conftest import create_empty_ooxml, create_fake_pptx, zip_names

def test_dedup_removes_duplicate_media(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    pptx_path = input_dir / "duplicates.pptx"
    duplicate_data = sample_images["big_png"].read_bytes()

    create_fake_pptx(
        pptx_path,
        {
            "image1.png": duplicate_data,
            "image2.png": duplicate_data,
        },
    )

    stats = process_file(pptx_path, base_cfg)

    assert stats["found"] == 2
    assert stats["saved"] == 1
    assert stats["duplicates"] == 1

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "duplicates.zip"
    assert output_zip.exists()

    assert len(zip_names(output_zip)) == 1


def test_dimension_filter_removes_small_icons(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    base_cfg["filters"]["min_kb"] = 1
    base_cfg["filters"]["min_width"] = 100
    base_cfg["filters"]["min_height"] = 100

    pptx_path = input_dir / "filters.pptx"

    create_fake_pptx(
        pptx_path,
        {
            "big.png": sample_images["big_png"].read_bytes(),
            "icon.png": sample_images["small_icon"].read_bytes(),
        },
    )

    stats = process_file(pptx_path, base_cfg)

    assert stats["found"] == 2
    assert stats["saved"] == 1
    assert stats["filtered_dims"] == 1

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "filters.zip"
    assert output_zip.exists()

    names = zip_names(output_zip)
    assert len(names) == 1


def test_empty_ooxml_does_not_create_zip(tmp_path: Path, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    pptx_path = input_dir / "empty.pptx"
    create_empty_ooxml(pptx_path)

    stats = process_file(pptx_path, base_cfg)

    assert stats["found"] == 0
    assert stats["saved"] == 0

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "empty.zip"
    assert not output_zip.exists()


def test_corrupt_file_returns_error_and_cleans_temp(tmp_path: Path, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    corrupt_path = input_dir / "corrupt.xlsx"
    corrupt_path.write_bytes(b"this is not a valid zip file")

    stats = process_file(corrupt_path, base_cfg)

    assert "error" in stats

    temp_folder = Path(base_cfg["paths"]["temp_dir"]) / "corrupt"
    assert not temp_folder.exists()


def test_list_input_files_recursive(tmp_path: Path, sample_images):
    input_dir = tmp_path / "input"
    subfolder = input_dir / "subfolder"
    subfolder.mkdir(parents=True)

    pptx_path = subfolder / "nested.pptx"
    create_fake_pptx(
        pptx_path,
        {
            "image1.png": sample_images["big_png"].read_bytes(),
        },
    )

    non_recursive = list_input_files(input_dir, recursive=False)
    recursive = list_input_files(input_dir, recursive=True)

    assert non_recursive == []
    assert recursive == [pptx_path]


def test_format_folder_creates_folder_output(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    base_cfg["output"]["format"] = "folder"

    pptx_path = input_dir / "folder_output.pptx"
    create_fake_pptx(
        pptx_path,
        {
            "image1.png": sample_images["big_png"].read_bytes(),
        },
    )

    stats = process_file(pptx_path, base_cfg)

    assert stats["saved"] == 1

    output_folder = Path(base_cfg["paths"]["output_dir"]) / "folder_output"
    assert output_folder.exists()
    assert output_folder.is_dir()

    extracted_files = list(output_folder.iterdir())
    assert len(extracted_files) == 1