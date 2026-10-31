
"""
Pruebas del procesamiento OCR unificado.

Comprueba documentos reales y verifica
que no se ejecute OCR repetidamente.
"""

import pytest
import pymupdf

from doclab.document_engine.ocr_unified import (
    procesar_ocr_unificado
)


def crear_imagen_con_texto(texto):
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


def test_documento_digital_sin_ocr(tmp_path):
    ruta = tmp_path / "digital.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_text(
            (72, 72),
            "TEXTO DIGITAL DOCLAB"
        )
        documento.save(str(ruta))

    # No deberia necesitar modelos OCR.
    resultado = procesar_ocr_unificado(
        ruta,
        carpeta_tessdata=tmp_path / "no_existe"
    )

    assert resultado.documento.total_paginas == 1

    assert (
        resultado.documento.paginas[0].metodo
        == "digital"
    )

    assert (
        "TEXTO DIGITAL DOCLAB"
        in resultado.documento.paginas[0].texto
    )

    assert resultado.paginas_posicionadas == ()


def test_documento_mixto_y_escaneado(
    tmp_path,
    monkeypatch
):
    ruta = tmp_path / "mixto.pdf"

    imagen_mixta = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    with pymupdf.open() as documento:

        pagina_uno = documento.new_page(
            width=600,
            height=500
        )

        pagina_uno.insert_text(
            (50, 60),
            "ENCABEZADO DIGITAL",
            fontsize=20
        )

        pagina_uno.insert_image(
            pymupdf.Rect(20, 130, 580, 320),
            stream=imagen_mixta
        )

        pagina_dos = documento.new_page(
            width=600,
            height=200
        )

        pagina_dos.insert_image(
            pagina_dos.rect,
            stream=imagen_escaneada
        )

        documento.save(str(ruta))

    # Instrumentar PyMuPDF para contar llamadas
    # al reconocimiento OCR real.
    funcion_original = pymupdf.Page.get_textpage_ocr
    llamadas = []

    def contar_ocr(self, *args, **opciones):
        llamadas.append(
            self.number + 1
        )

        return funcion_original(
            self,
            *args,
            **opciones
        )

    monkeypatch.setattr(
        pymupdf.Page,
        "get_textpage_ocr",
        contar_ocr
    )

    resultado = procesar_ocr_unificado(ruta)

    # Dos paginas requieren OCR:
    # exactamente una llamada por pagina.
    assert llamadas == [1, 2]

    assert tuple(
        pagina.metodo
        for pagina in resultado.documento.paginas
    ) == (
        "ocr_parcial",
        "ocr_completo"
    )

    assert len(resultado.paginas_posicionadas) == 2

    fragmentos_mixtos = (
        resultado.paginas_posicionadas[0].fragmentos
    )

    origenes = {
        fragmento.origen
        for fragmento in fragmentos_mixtos
    }

    assert origenes == {"digital", "ocr"}

    texto_mixto = " ".join(
        fragmento.texto
        for fragmento in fragmentos_mixtos
    ).upper()

    assert "ENCABEZADO DIGITAL" in texto_mixto
    assert "CODIGO" in texto_mixto
    assert "5678" in texto_mixto

    texto_escaneado = (
        resultado.documento.paginas[1].texto.upper()
    )

    assert "FACTURA" in texto_escaneado
    assert "DOCLAB" in texto_escaneado
    assert "2026" in texto_escaneado


def test_pagina_vacia_sin_ocr(tmp_path):
    ruta = tmp_path / "vacio.pdf"

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(str(ruta))

    resultado = procesar_ocr_unificado(
        ruta,
        carpeta_tessdata=tmp_path / "no_existe"
    )

    assert resultado.documento.paginas[0].metodo == "vacia"
    assert resultado.documento.paginas[0].texto == ""
    assert resultado.paginas_posicionadas == ()


def test_rechazar_dpi_invalido():
    with pytest.raises(ValueError):
        procesar_ocr_unificado(
            "documento.pdf",
            dpi=0
        )
