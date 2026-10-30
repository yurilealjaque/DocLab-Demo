
import pymupdf

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)


def crear_imagen():
    """Crea una imagen de prueba en memoria."""

    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)

    return imagen


def test_pagina_escaneada_simulada(tmp_path):
    ruta = tmp_path / "escaneo.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pagina.rect,
            pixmap=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "sin_texto"
    assert resultado.paginas_posibles_escaneos == (1,)


def test_imagen_pequena_no_es_escaneo(tmp_path):
    ruta = tmp_path / "imagen_pequena.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pymupdf.Rect(0, 0, 50, 50),
            pixmap=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.paginas_con_imagenes == (1,)
    assert resultado.paginas_posibles_escaneos == ()


def test_texto_e_imagen_grande(tmp_path):
    ruta = tmp_path / "texto_imagen.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pagina.rect,
            pixmap=crear_imagen()
        )

        pagina.insert_text(
            (20, 20),
            "Texto digital"
        )

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.paginas_con_texto == (1,)
    assert resultado.paginas_con_texto_e_imagenes == (1,)
    assert resultado.paginas_posibles_escaneos == ()


def test_documento_con_paginas_diferentes(tmp_path):
    ruta = tmp_path / "documento_mixto.pdf"

    with pymupdf.open() as documento:

        # Pagina 1: texto digital.
        pagina_uno = documento.new_page(
            width=200,
            height=200
        )

        pagina_uno.insert_text(
            (20, 20),
            "Primera pagina"
        )

        # Pagina 2: imagen completa.
        pagina_dos = documento.new_page(
            width=200,
            height=200
        )

        pagina_dos.insert_image(
            pagina_dos.rect,
            pixmap=crear_imagen()
        )

        # Pagina 3: pagina vacia.
        documento.new_page(
            width=200,
            height=200
        )

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.total_paginas == 3
    assert resultado.clasificacion == "mixto"
    assert resultado.paginas_con_texto == (1,)
    assert resultado.paginas_sin_texto == (2, 3)
    assert resultado.paginas_con_imagenes == (2,)
    assert resultado.paginas_posibles_escaneos == (2,)
