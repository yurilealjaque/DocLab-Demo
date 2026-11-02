"""Pruebas del motor de brillo y contraste sin escritura en disco."""

import pytest
from PySide6.QtGui import QImage, QColor

from doclab.document_engine.image_adjustments import (
    ErrorAjusteImagen,
    ajustar_brillo_contraste,
)


def imagen_de_prueba():
    imagen = QImage(2, 1, QImage.Format.Format_ARGB32)
    imagen.setPixelColor(0, 0, QColor(60, 90, 120, 80))
    imagen.setPixelColor(1, 0, QColor(190, 170, 150, 210))
    return imagen


def test_sin_ajustes_conserva_pixeles():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original)
    assert resultado.pixelColor(0, 0) == original.pixelColor(0, 0)
    assert resultado.pixelColor(1, 0) == original.pixelColor(1, 0)
    assert resultado.size() == original.size()


def test_brillo_positivo_aclara():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original, brillo=20)
    assert resultado.pixelColor(0, 0).red() > original.pixelColor(0, 0).red()


def test_brillo_negativo_oscurece():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original, brillo=-20)
    assert resultado.pixelColor(0, 0).red() < original.pixelColor(0, 0).red()


def test_contraste_positivo_separa_valores():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original, contraste=50)
    separacion_anterior = original.pixelColor(1, 0).red() - original.pixelColor(0, 0).red()
    separacion_nueva = resultado.pixelColor(1, 0).red() - resultado.pixelColor(0, 0).red()
    assert separacion_nueva > separacion_anterior


def test_contraste_negativo_acerca_valores():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original, contraste=-50)
    separacion_anterior = original.pixelColor(1, 0).red() - original.pixelColor(0, 0).red()
    separacion_nueva = resultado.pixelColor(1, 0).red() - resultado.pixelColor(0, 0).red()
    assert separacion_nueva < separacion_anterior


def test_preserva_transparencia():
    original = imagen_de_prueba()
    resultado = ajustar_brillo_contraste(original, brillo=25, contraste=25)
    assert [resultado.pixelColor(x, 0).alpha() for x in range(2)] == [80, 210]


def test_no_modifica_imagen_original():
    original = imagen_de_prueba()
    previo = original.copy()
    resultado = ajustar_brillo_contraste(original, brillo=40)
    assert original == previo
    assert resultado != original


@pytest.mark.parametrize("brillo,contraste", [(-101, 0), (101, 0), (0, -101), (0, 101), (2.5, 0), (True, 0)])
def test_rechaza_parametros_invalidos(brillo, contraste):
    with pytest.raises(ErrorAjusteImagen):
        ajustar_brillo_contraste(imagen_de_prueba(), brillo, contraste)


def test_rechaza_imagen_nula():
    with pytest.raises(ErrorAjusteImagen):
        ajustar_brillo_contraste(QImage())


def test_brillo_extremo_limita_canales():
    original = imagen_de_prueba()
    blanco = ajustar_brillo_contraste(original, brillo=100)
    negro = ajustar_brillo_contraste(original, brillo=-100)
    assert blanco.pixelColor(0, 0).red() == 255
    assert negro.pixelColor(0, 0).red() == 0
