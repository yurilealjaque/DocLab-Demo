
import pytest
import pymupdf

from doclab.document_engine.pdf_validator import (
    validar_pdf,
    PDFProtegidoError,
    PDFCorruptoError,
)


def test_pdf_valido(tmp_path):
    ruta = tmp_path / "valido.pdf"

    documento = pymupdf.open()
    documento.new_page()
    documento.save(str(ruta))
    documento.close()

    paginas = validar_pdf(ruta)

    assert paginas == 1


def test_pdf_inexistente(tmp_path):
    ruta = tmp_path / "inexistente.pdf"

    with pytest.raises(FileNotFoundError):
        validar_pdf(ruta)


def test_archivo_no_pdf(tmp_path):
    ruta = tmp_path / "falso.pdf"

    ruta.write_text(
        "Esto no es un documento PDF",
        encoding="utf-8"
    )

    with pytest.raises(PDFCorruptoError):
        validar_pdf(ruta)


def test_pdf_con_contrasena(tmp_path):
    ruta = tmp_path / "protegido.pdf"

    documento = pymupdf.open()
    documento.new_page()

    documento.save(
        str(ruta),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        user_pw="clave123",
        owner_pw="administrador456"
    )

    documento.close()

    with pytest.raises(PDFProtegidoError):
        validar_pdf(ruta)
