
"""
Pruebas del servicio de conversion OCR.

Comprueba:
- Conversion digital real.
- Conversion escaneada real.
- Proteccion de archivos existentes.
"""

import pytest
import pymupdf

from docx import Document

from doclab.services.ocr_conversion_service import (
    ServicioConversionOCR,
    ResultadoConversionOCR
)


def crear_imagen_con_texto(texto):
    """
    Genera una imagen PNG con texto.
    """

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=600,
            height=200
        )

        pagina.insert_text(
            (35, 110),
            texto,
            fontsize=28
        )

        imagen = pagina.get_pixmap(
            dpi=300,
            alpha=False
        )

        return imagen.tobytes("png")


def obtener_texto_word(ruta):
    """
    Abre un DOCX y obtiene el texto de sus parrafos.
    """

    documento = Document(str(ruta))

    return " ".join(
        " ".join(
            parrafo.text
            for parrafo in documento.paragraphs
        ).upper().split()
    )


def test_servicio_convierte_pdf_digital(tmp_path):
    origen = tmp_path / "digital.pdf"
    destino = tmp_path / "digital.docx"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "DOCUMENTO DIGITAL DOCLAB"
        )

        documento.save(str(origen))

    servicio = ServicioConversionOCR()

    resultado = servicio.convertir(
        origen,
        destino
    )

    assert isinstance(
        resultado,
        ResultadoConversionOCR
    )

    assert resultado.ruta_destino == str(destino)
    assert resultado.total_paginas == 1
    assert resultado.paginas_con_ocr == 0
    assert resultado.imagenes_exportadas == 0

    assert destino.is_file()

    texto = obtener_texto_word(destino)

    assert "DOCUMENTO DIGITAL DOCLAB" in texto


def test_servicio_convierte_pdf_escaneado(tmp_path):
    origen = tmp_path / "escaneado.pdf"
    destino = tmp_path / "escaneado.docx"

    imagen = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=600,
            height=200
        )

        pagina.insert_image(
            pagina.rect,
            stream=imagen
        )

        documento.save(str(origen))

    servicio = ServicioConversionOCR()

    resultado = servicio.convertir(
        origen,
        destino
    )

    assert resultado.total_paginas == 1
    assert resultado.paginas_con_ocr == 1
    assert resultado.imagenes_exportadas == 0

    texto = obtener_texto_word(destino)

    assert "FACTURA" in texto
    assert "DOCLAB" in texto
    assert "2026" in texto


def test_servicio_no_sobrescribe_word(tmp_path):
    origen = tmp_path / "origen.pdf"
    destino = tmp_path / "existente.docx"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "DOCUMENTO ORIGINAL"
        )

        documento.save(str(origen))

    destino.write_bytes(b"Contenido anterior")

    servicio = ServicioConversionOCR()

    with pytest.raises(FileExistsError):
        servicio.convertir(
            origen,
            destino
        )

    assert destino.read_bytes() == b"Contenido anterior"
