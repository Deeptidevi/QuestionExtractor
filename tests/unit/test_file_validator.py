import io
import pytest
from app.processing.file_validator import FileValidator
from app.core.exceptions import InvalidFileException, UnsupportedFileTypeException, FileTooLargeException


def test_validate_valid_pdf():
    pdf_content = b"%PDF-1.4 test document stream"
    stream = io.BytesIO(pdf_content)
    mime, ext = FileValidator.validate_upload(
        file_obj=stream,
        filename="exam.pdf",
        content_type="application/pdf",
        file_size=len(pdf_content),
    )
    assert mime == "application/pdf"
    assert ext == ".pdf"


def test_validate_valid_png():
    png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    stream = io.BytesIO(png_content)
    mime, ext = FileValidator.validate_upload(
        file_obj=stream,
        filename="diagram.png",
        content_type="image/png",
        file_size=len(png_content),
    )
    assert mime == "image/png"
    assert ext == ".png"


def test_validate_invalid_extension():
    content = b"executable binary"
    stream = io.BytesIO(content)
    with pytest.raises(UnsupportedFileTypeException):
        FileValidator.validate_upload(
            file_obj=stream,
            filename="virus.exe",
            content_type="application/x-msdownload",
            file_size=len(content),
        )


def test_validate_empty_file():
    stream = io.BytesIO(b"")
    with pytest.raises(InvalidFileException):
        FileValidator.validate_upload(
            file_obj=stream,
            filename="empty.pdf",
            content_type="application/pdf",
            file_size=0,
        )


def test_validate_oversized_file(monkeypatch):
    content = b"%PDF-1.4 test"
    stream = io.BytesIO(content)
    with pytest.raises(FileTooLargeException):
        FileValidator.validate_upload(
            file_obj=stream,
            filename="huge.pdf",
            content_type="application/pdf",
            file_size=100 * 1024 * 1024,  # 100MB > 50MB limit
        )
