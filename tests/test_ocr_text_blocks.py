
"""
Pruebas del extractor de texto OCR posicionado.

Incluye reconocimiento OCR real.
"""

import pytest
import pymupdf

from doclab.document_engine.ocr_engine import (
    RecursosOCRNoDisponiblesError
)

from doclab.document_engine.ocr_text_blocks import (
    extraer_texto_posicionado
)


def crear_imagen_con_texto(texto):
    """
    Genera una imagen PNG que contiene palabras.
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


def test_ocr_real_con_coordenadas(tmp_path):
    ruta = tmp_path / "escaneado.pdf"

    datos_imagen = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=600,
            height=200
        )

        pagina.insert_image(
            pagina.rect,
            stream=datos_imagen
        )

        documento.save(str(ruta))

    resultado = extraer_texto_posicionado(
        ruta,
        numero_pagina=1,
        completo=True
    )

    assert resultado.numero_pagina == 1
    assert len(resultado.fragmentos) > 0

    texto = " ".join(
        fragmento.texto
        for fragmento in resultado.fragmentos
    ).upper()

    assert "FACTURA" in texto
    assert "DOCLAB" in texto
    assert "2026" in texto

    assert all(
        fragmento.origen == "ocr"
        for fragmento in resultado.fragmentos
    )

    for fragmento in resultado.fragmentos:

        x0, y0, x1, y1 = fragmento.coordenadas

        assert 0 <= x0 < x1 <= 600
        assert 0 <= y0 < y1 <= 200


def test_ocr_parcial_distingue_origenes(tmp_path):
    ruta = tmp_path / "mixto.pdf"

    datos_imagen = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=600,
            height=500
        )

        pagina.insert_text(
            (50, 60),
            "ENCABEZADO DIGITAL",
            fontsize=20
        )

        pagina.insert_image(
            pymupdf.Rect(20, 130, 580, 320),
            stream=datos_imagen
        )

        documento.save(str(ruta))

    resultado = extraer_texto_posicionado(
        ruta,
        numero_pagina=1,
        completo=False
    )

    digitales = [
        fragmento
        for fragmento in resultado.fragmentos
        if fragmento.origen == "digital"
    ]

    reconocidos = [
        fragmento
        for fragmento in resultado.fragmentos
        if fragmento.origen == "ocr"
    ]

    texto_digital = " ".join(
        fragmento.texto for fragmento in digitales
    ).upper()

    texto_ocr = " ".join(
        fragmento.texto for fragmento in reconocidos
    ).upper()

    assert "ENCABEZADO DIGITAL" in texto_digital

    assert "CODIGO" in texto_ocr
    assert "IMAGEN" in texto_ocr
    assert "5678" in texto_ocr

    # Verificar que sus posiciones son distintas.
    assert min(
        fragmento.coordenadas[1]
        for fragmento in digitales
    ) < min(
        fragmento.coordenadas[1]
        for fragmento in reconocidos
    )


def test_rechazar_numero_pagina_invalido():
    with pytest.raises(ValueError):
        extraer_texto_posicionado(
            "documento.pdf",
            numero_pagina=0
        )


def test_rechazar_dpi_invalido():
    with pytest.raises(ValueError):
        extraer_texto_posicionado(
            "documento.pdf",
            numero_pagina=1,
            dpi=0
        )


def test_rechazar_pagina_inexistente(tmp_path):
    ruta = tmp_path / "una_pagina.pdf"

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(str(ruta))

    with pytest.raises(ValueError):
        extraer_texto_posicionado(
            ruta,
            numero_pagina=2
        )


def test_rechazar_recursos_faltantes(tmp_path):
    ruta = tmp_path / "digital.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_text(
            (72, 72),
            "Texto de prueba"
        )
        documento.save(str(ruta))

    with pytest.raises(RecursosOCRNoDisponiblesError):
        extraer_texto_posicionado(
            ruta,
            numero_pagina=1,
            carpeta_tessdata=tmp_path / "no_existe"
        )
