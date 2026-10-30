
import pytest
import pymupdf

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError
)


def crear_pdf(ruta, paginas):
    """Crea un PDF de prueba."""

    with pymupdf.open() as documento:

        for tiene_texto in paginas:
            pagina = documento.new_page()

            if tiene_texto:
                pagina.insert_text(
                    (72, 72),
                    "Documento de prueba DocLab"
                )

        documento.save(str(ruta))


def test_pdf_con_texto(tmp_path):
    ruta = tmp_path / "digital.pdf"
    crear_pdf(ruta, [True, True])

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "con_texto"
    assert resultado.total_paginas == 2
    assert resultado.paginas_con_texto == (1, 2)


def test_pdf_sin_texto(tmp_path):
    ruta = tmp_path / "sin_texto.pdf"
    crear_pdf(ruta, [False, False])

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "sin_texto"
    assert resultado.paginas_sin_texto == (1, 2)


def test_pdf_mixto(tmp_path):
    ruta = tmp_path / "mixto.pdf"
    crear_pdf(ruta, [True, False, True])

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "mixto"
    assert resultado.paginas_con_texto == (1, 3)
    assert resultado.paginas_sin_texto == (2,)


def test_pdf_inexistente(tmp_path):
    ruta = tmp_path / "inexistente.pdf"

    with pytest.raises(FileNotFoundError):
        inspeccionar_contenido_pdf(ruta)


def test_pdf_corrupto(tmp_path):
    ruta = tmp_path / "corrupto.pdf"
    ruta.write_text("Esto no es un PDF")

    with pytest.raises(PDFCorruptoError):
        inspeccionar_contenido_pdf(ruta)


def test_pdf_protegido(tmp_path):
    ruta = tmp_path / "protegido.pdf"

    with pymupdf.open() as documento:
        documento.new_page()

        documento.save(
            str(ruta),
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            user_pw="clave123",
            owner_pw="administrador456"
        )

    with pytest.raises(PDFProtegidoError):
        inspeccionar_contenido_pdf(ruta)
