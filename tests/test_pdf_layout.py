
import pytest
import pymupdf

from doclab.document_engine.pdf_layout import (
    analizar_estructura_pdf
)


def crear_imagen():
    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)
    return imagen


def test_detectar_bloque_texto(tmp_path):
    ruta = tmp_path / "texto.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "Hola DocLab"
        )

        documento.save(str(ruta))

    resultado = analizar_estructura_pdf(ruta)

    assert resultado.total_paginas == 1
    assert len(resultado.bloques) == 1
    assert resultado.bloques[0].tipo == "texto"
    assert "Hola DocLab" in resultado.bloques[0].texto


def test_detectar_bloque_imagen(tmp_path):
    ruta = tmp_path / "imagen.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=300,
            height=300
        )

        pagina.insert_image(
            pymupdf.Rect(50, 50, 150, 150),
            pixmap=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = analizar_estructura_pdf(ruta)

    assert len(resultado.bloques) == 1
    assert resultado.bloques[0].tipo == "imagen"

    assert resultado.bloques[0].coordenadas == pytest.approx(
        (50, 50, 150, 150)
    )


def test_texto_e_imagen(tmp_path):
    ruta = tmp_path / "mixto.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=300,
            height=300
        )

        pagina.insert_text(
            (50, 50),
            "Titulo DocLab"
        )

        pagina.insert_image(
            pymupdf.Rect(50, 100, 150, 200),
            pixmap=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = analizar_estructura_pdf(ruta)

    tipos = [
        bloque.tipo
        for bloque in resultado.bloques
    ]

    assert "texto" in tipos
    assert "imagen" in tipos


def test_pagina_vacia(tmp_path):
    ruta = tmp_path / "vacio.pdf"

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(str(ruta))

    resultado = analizar_estructura_pdf(ruta)

    assert resultado.total_paginas == 1
    assert resultado.bloques == ()


def test_documento_multipagina(tmp_path):
    ruta = tmp_path / "multipagina.pdf"

    with pymupdf.open() as documento:
        pagina_uno = documento.new_page()
        pagina_uno.insert_text(
            (72, 72),
            "Primera pagina"
        )

        pagina_dos = documento.new_page()
        pagina_dos.insert_text(
            (72, 72),
            "Segunda pagina"
        )

        documento.save(str(ruta))

    resultado = analizar_estructura_pdf(ruta)

    assert resultado.total_paginas == 2

    numeros = tuple(
        bloque.numero_pagina
        for bloque in resultado.bloques
    )

    assert numeros == (1, 2)
