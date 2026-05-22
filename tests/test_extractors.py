from pathlib import Path
from document_image_extractor.pipeline import process_file
from .conftest import (create_docx, create_pdf, create_fake_pptx, create_fake_xlsx, zip_names)

def test_docx_extracts_real_extensions(tmp_path: Path, sample_images, base_cfg): 
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    docx_path = input_dir / "mixed.docx"
    create_docx(docx_path, [sample_images["photo_jpg"], sample_images["big_png"]])

    stats = process_file(docx_path, base_cfg)

    assert stats["saved"] == 2

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "mixed.zip"
    assert output_zip.exists()

    names = zip_names(output_zip)

    assert any(name.endswith(".jpg") for name in names)
    assert any(name.endswith(".png") for name in names)

def test_pdf_extracts_image(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    pdf_path = input_dir / "sample.pdf"
    create_pdf(pdf_path, sample_images["big_png"])

    stats = process_file(pdf_path, base_cfg)

    assert stats["found"] >= 1
    assert stats["saved"] >= 1

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "sample.zip"
    assert output_zip.exists()

def test_pptx_extracts_media_images(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    pptx_path = input_dir / "slides.pptx"

    create_fake_pptx(
        pptx_path,
        {
            "image1.png": sample_images["big_png"].read_bytes(),
            "image2.jpg": sample_images["photo_jpg"].read_bytes(),
        },
    )

    stats = process_file(pptx_path, base_cfg)

    assert stats["found"] == 2
    assert stats["saved"] == 2

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "slides.zip"
    assert output_zip.exists()

    names = zip_names(output_zip)
    assert any(name.endswith(".png") for name in names)
    assert any(name.endswith(".jpg") for name in names)

def test_xlsx_extracts_media_images(tmp_path: Path, sample_images, base_cfg):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    xlsx_path = input_dir / "book.xlsx"

    create_fake_xlsx(
        xlsx_path,
        {
            "image1.png": sample_images["big_png"].read_bytes(),
            "image2.jpg": sample_images["photo_jpg"].read_bytes(),
        },
    )

    stats = process_file(xlsx_path, base_cfg)

    assert stats["found"] == 2
    assert stats["saved"] == 2

    output_zip = Path(base_cfg["paths"]["output_dir"]) / "book.zip"
    assert output_zip.exists()