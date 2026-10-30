
import pytest
import pymupdf

from doclab.document_engine.image_coverage import (
    calcular_cobertura_imagen,
    es_posible_escaneo,
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


def test_pagina_sin_imagenes():
    with pymupdf.open() as documento:

        pagina = documento.new_page(
            width=200,
            height=200
        )

        cobertura = calcular_cobertura_imagen(pagina)

        assert cobertura == 0.0
        assert es_posible_escaneo(pagina) is False


def test_imagen_pequena():
    with pymupdf.open() as documento:

        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pymupdf.Rect(0, 0, 100, 100),
            pixmap=crear_imagen()
        )

        cobertura = calcular_cobertura_imagen(pagina)

        assert cobertura == pytest.approx(0.25)
        assert es_posible_escaneo(pagina) is False


def test_imagen_pagina_completa():
    with pymupdf.open() as documento:

        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pagina.rect,
            pixmap=crear_imagen()
        )

        cobertura = calcular_cobertura_imagen(pagina)

        assert cobertura == pytest.approx(1.0)
        assert es_posible_escaneo(pagina) is True


def test_umbral_personalizado():
    with pymupdf.open() as documento:

        pagina = documento.new_page(
            width=200,
            height=200
        )

        pagina.insert_image(
            pymupdf.Rect(0, 0, 150, 200),
            pixmap=crear_imagen(),
             keep_proportion=False
        )

        cobertura = calcular_cobertura_imagen(pagina)

        assert cobertura == pytest.approx(0.75)

        assert es_posible_escaneo(
            pagina, umbral=0.70
        ) is True

        assert es_posible_escaneo(
            pagina, umbral=0.80
        ) is False


def test_umbral_invalido():
    with pymupdf.open() as documento:

        pagina = documento.new_page()

        with pytest.raises(ValueError):
            es_posible_escaneo(pagina, umbral=0)

        with pytest.raises(ValueError):
            es_posible_escaneo(pagina, umbral=1.5)
