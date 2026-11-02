"""Pruebas de rotación aplicada realmente al PDF generado."""

import pytest
import pymupdf

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine.photo_manager import GestorFotografias
from doclab.document_engine.photos_to_pdf import (
    _convertir_imagen_a_png,
    generar_pdf_fotografias,
)


def crear_imagen(ruta, ancho=120, alto=80):
    imagen = QImage(ancho, alto, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.white)
    assert imagen.save(str(ruta), "PNG")
    return ruta


def dimensiones_pdf(ruta_pdf):
    with pymupdf.open(str(ruta_pdf)) as documento:
        return [
            (round(pagina.rect.width), round(pagina.rect.height))
            for pagina in documento
        ]


def test_pdf_sin_rotacion_conserva_dimensiones(tmp_path):
    imagen = crear_imagen(tmp_path / "original.png")
    gestor = GestorFotografias()
    gestor.agregar_fotografia(imagen)
    destino = tmp_path / "original.pdf"

    resultado = generar_pdf_fotografias(gestor, destino)

    assert resultado.numero_paginas == 1
    assert dimensiones_pdf(destino) == [(120, 80)]


@pytest.mark.parametrize("giros,dimensiones", [
    (1, (80, 120)),
    (2, (120, 80)),
    (3, (80, 120)),
    (4, (120, 80)),
])
def test_pdf_respeta_giros_a_derecha(tmp_path, giros, dimensiones):
    imagen = crear_imagen(tmp_path / "imagen.png")
    gestor = GestorFotografias()
    gestor.agregar_fotografia(imagen)
    for _ in range(giros):
        gestor.rotar_derecha(0)

    destino = tmp_path / "girado.pdf"
    generar_pdf_fotografias(gestor, destino)

    assert dimensiones_pdf(destino) == [dimensiones]


def test_pdf_respeta_giro_a_izquierda(tmp_path):
    imagen = crear_imagen(tmp_path / "imagen.png")
    gestor = GestorFotografias()
    gestor.agregar_fotografia(imagen)
    assert gestor.rotar_izquierda(0) == 270

    destino = tmp_path / "izquierda.pdf"
    generar_pdf_fotografias(gestor, destino)
    assert dimensiones_pdf(destino) == [(80, 120)]


def test_rotaciones_independientes_y_orden(tmp_path):
    rutas = [
        crear_imagen(tmp_path / "uno.png", 120, 80),
        crear_imagen(tmp_path / "dos.png", 90, 60),
    ]
    gestor = GestorFotografias()
    gestor.agregar_fotografias(rutas)
    gestor.rotar_derecha(0)
    gestor.bajar_fotografia(0)

    destino = tmp_path / "multipagina.pdf"
    generar_pdf_fotografias(gestor, destino)

    assert dimensiones_pdf(destino) == [(90, 60), (80, 120)]


def test_giro_no_modifica_imagen_original(tmp_path):
    ruta = crear_imagen(tmp_path / "original.png")
    contenido_antes = ruta.read_bytes()
    gestor = GestorFotografias()
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)

    generar_pdf_fotografias(gestor, tmp_path / "resultado.pdf")

    assert ruta.read_bytes() == contenido_antes


def test_rotacion_invalida_se_rechaza(tmp_path):
    ruta = crear_imagen(tmp_path / "original.png")
    with pytest.raises(ValueError, match="rotación"):
        _convertir_imagen_a_png(ruta, 45)
    with pytest.raises(ValueError):
        _convertir_imagen_a_png(ruta, True)


def test_pixeles_realmente_rotados(tmp_path):
    """La rotación debe afectar el contenido, no solo el tamaño de página."""
    ruta = tmp_path / "esquinas.png"
    imagen = QImage(100, 60, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.white)
    # Esquina superior izquierda roja, resto blanco.
    for x in range(20):
        for y in range(20):
            imagen.setPixelColor(x, y, Qt.GlobalColor.red)
    assert imagen.save(str(ruta), "PNG")

    gestor = GestorFotografias()
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)
    destino = tmp_path / "girado.pdf"
    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(str(destino)) as documento:
        pixmap = documento[0].get_pixmap(alpha=False)
        assert (pixmap.width, pixmap.height) == (60, 100)
        # El rojo de la esquina superior izquierda debe estar ahora arriba a la derecha.
        def pixel(x, y):
            pos = (y * pixmap.width + x) * pixmap.n
            return tuple(pixmap.samples[pos:pos + 3])

        r, g, b = pixel(50, 10)
        assert r > 220 and g < 50 and b < 50
        r, g, b = pixel(10, 10)
        assert r > 220 and g > 220 and b > 220
