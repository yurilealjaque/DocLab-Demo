
import pymupdf

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)


def crear_imagen():
    """
    Crea una imagen en memoria para las pruebas.
    No necesita archivos externos.
    """

    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 40, 40),
        False
    )

    imagen.clear_with(180)

    return imagen


def agregar_imagen(pagina):
    """
    Inserta una imagen dentro de una pagina PDF.
    """

    imagen = crear_imagen()

    pagina.insert_image(
        pymupdf.Rect(100, 100, 200, 200),
        pixmap=imagen
    )


def test_pdf_solo_texto(tmp_path):
    ruta = tmp_path / "solo_texto.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_text((72, 72), "Texto digital")
        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "con_texto"
    assert resultado.paginas_con_imagenes == ()
    assert resultado.total_imagenes == 0


def test_pdf_solo_imagen(tmp_path):
    ruta = tmp_path / "solo_imagen.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        agregar_imagen(pagina)
        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "sin_texto"
    assert resultado.paginas_con_imagenes == (1,)
    assert resultado.total_imagenes == 1


def test_pdf_texto_e_imagen(tmp_path):
    ruta = tmp_path / "texto_imagen.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "Documento con texto e imagen"
        )

        agregar_imagen(pagina)
        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "con_texto"
    assert resultado.paginas_con_imagenes == (1,)
    assert resultado.paginas_con_texto_e_imagenes == (1,)


def test_pdf_varias_paginas(tmp_path):
    ruta = tmp_path / "varias_paginas.pdf"

    with pymupdf.open() as documento:

        pagina_uno = documento.new_page()
        pagina_uno.insert_text((72, 72), "Pagina uno")

        pagina_dos = documento.new_page()
        agregar_imagen(pagina_dos)

        pagina_tres = documento.new_page()
        pagina_tres.insert_text((72, 72), "Pagina tres")
        agregar_imagen(pagina_tres)

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.total_paginas == 3
    assert resultado.clasificacion == "mixto"
    assert resultado.paginas_con_texto == (1, 3)
    assert resultado.paginas_sin_texto == (2,)
    assert resultado.paginas_con_imagenes == (2, 3)
    assert resultado.paginas_con_texto_e_imagenes == (3,)
    assert resultado.total_imagenes == 2


def test_pdf_dos_imagenes(tmp_path):
    ruta = tmp_path / "dos_imagenes.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        imagen = crear_imagen()

        pagina.insert_image(
            pymupdf.Rect(50, 50, 100, 100),
            pixmap=imagen
        )

        pagina.insert_image(
            pymupdf.Rect(150, 150, 200, 200),
            pixmap=imagen
        )

        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.paginas_con_imagenes == (1,)
    assert resultado.total_imagenes == 2


def test_pdf_pagina_vacia(tmp_path):
    ruta = tmp_path / "pagina_vacia.pdf"

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(str(ruta))

    resultado = inspeccionar_contenido_pdf(ruta)

    assert resultado.clasificacion == "sin_texto"
    assert resultado.paginas_con_imagenes == ()
    assert resultado.paginas_con_texto_e_imagenes == ()
    assert resultado.total_imagenes == 0
