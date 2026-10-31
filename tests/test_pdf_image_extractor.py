
import pytest
import pymupdf

from doclab.document_engine.pdf_image_extractor import (
    extraer_imagenes_pdf
)


def crear_imagen():
    """
    Crea una imagen PNG en memoria.
    """

    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)

    return imagen.tobytes("png")


def test_extraer_una_imagen(tmp_path):
    ruta = tmp_path / "imagen.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=300,
            height=300
        )

        pagina.insert_image(
            pymupdf.Rect(50, 50, 150, 150),
            stream=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = extraer_imagenes_pdf(ruta)

    assert resultado.total_paginas == 1
    assert len(resultado.imagenes) == 1

    imagen = resultado.imagenes[0]

    assert imagen.numero_pagina == 1
    assert imagen.formato == "png"
    assert len(imagen.datos) > 0

    assert imagen.coordenadas == pytest.approx(
        (50, 50, 150, 150)
    )


def test_pdf_sin_imagenes(tmp_path):
    ruta = tmp_path / "solo_texto.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "Documento DocLab"
        )

        documento.save(str(ruta))

    resultado = extraer_imagenes_pdf(ruta)

    assert resultado.total_paginas == 1
    assert resultado.imagenes == ()


def test_imagenes_en_varias_paginas(tmp_path):
    ruta = tmp_path / "multipagina.pdf"

    with pymupdf.open() as documento:
        pagina_uno = documento.new_page()
        pagina_uno.insert_image(
            pymupdf.Rect(50, 50, 150, 150),
            stream=crear_imagen()
        )

        pagina_dos = documento.new_page()
        pagina_dos.insert_text(
            (72, 72),
            "Solo texto"
        )

        pagina_tres = documento.new_page()
        pagina_tres.insert_image(
            pymupdf.Rect(50, 50, 150, 150),
            stream=crear_imagen()
        )

        documento.save(str(ruta))

    resultado = extraer_imagenes_pdf(ruta)

    assert resultado.total_paginas == 3

    assert tuple(
        imagen.numero_pagina
        for imagen in resultado.imagenes
    ) == (1, 3)


def test_dos_apariciones_de_imagen(tmp_path):
    ruta = tmp_path / "dos_imagenes.pdf"

    datos = crear_imagen()

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=300,
            height=300
        )

        pagina.insert_image(
            pymupdf.Rect(20, 20, 100, 100),
            stream=datos
        )

        pagina.insert_image(
            pymupdf.Rect(150, 150, 230, 230),
            stream=datos
        )

        documento.save(str(ruta))

    resultado = extraer_imagenes_pdf(ruta)

    assert len(resultado.imagenes) == 2

    assert all(
        imagen.numero_pagina == 1
        for imagen in resultado.imagenes
    )


def test_pdf_inexistente(tmp_path):
    ruta = tmp_path / "no_existe.pdf"

    with pytest.raises(FileNotFoundError):
        extraer_imagenes_pdf(ruta)
