# Changelog

## v0.1.0

### Added
- CLI with argparse.
- Support for PDF, DOCX, PPTX and XLSX.
- Configurable filters using `config.json`.
- Size filter using `min_kb`.
- Optional dimension filters using `min_width` and `min_height`.
- Deduplication by hash.
- ZIP output per processed file.
- Folder output mode.
- Logging to console and file.
- Pytest test suite.
- Packaging support with `pyproject.toml`.
- Installable console command: `document-image-extractor`.

### Changed
- Refactored project into modules:
  - `extractors`
  - `utils`
  - `pipeline`
  - `report`

### Fixed
- DOCX images are saved with real extensions.
- PDF files are properly closed after processing.
- Temporary folders are cleaned after each file.