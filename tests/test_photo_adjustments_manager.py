"""Pruebas de ajustes por imagen en GestorFotografias (incremento 9B)."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine.image_adjustments import ErrorAjusteImagen
from doclab.document_engine.photo_manager import (
    FotografiaNoEncontradaError,
    FotografiaDuplicadaError,
    GestorFotografias,
)


def crear_imagen(ruta):
    imagen = QImage(120, 60, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.white)
    assert imagen.save(str(ruta), "PNG")
    return ruta


def preparar_gestor(tmp_path, cantidad=3):
    gestor = GestorFotografias()
    rutas = [crear_imagen(tmp_path / f"imagen_{n}.png") for n in range(cantidad)]
    assert gestor.agregar_fotografias(rutas) == cantidad
    return gestor, rutas


def test_valores_iniciales(tmp_path):
    gestor, _ = preparar_gestor(tmp_path)
    assert all(gestor.obtener_ajustes(i) == (0, 0) for i in range(3))


def test_establecer_y_consultar(tmp_path):
    gestor, _ = preparar_gestor(tmp_path)
    assert gestor.establecer_ajustes(1, 30, -15) == (30, -15)
    assert gestor.obtener_ajustes(1) == (30, -15)
    assert gestor.obtener_ajustes(0) == (0, 0)


def test_extremos_permitidos(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, 1)
    assert gestor.establecer_ajustes(0, -100, 100) == (-100, 100)
    assert gestor.establecer_ajustes(0, 100, -100) == (100, -100)


@pytest.mark.parametrize('brillo,contraste', [(-101, 0), (101, 0), (0, -101), (0, 101), (0.5, 0), (0, '20'), (True, 0)])
def test_rechazar_ajustes_invalidos_sin_cambios(tmp_path, brillo, contraste):
    gestor, _ = preparar_gestor(tmp_path, 1)
    gestor.establecer_ajustes(0, 25, -20)
    with pytest.raises(ErrorAjusteImagen):
        gestor.establecer_ajustes(0, brillo, contraste)
    assert gestor.obtener_ajustes(0) == (25, -20)


def test_ajustes_acompanan_imagen_al_reordenar(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path)
    gestor.establecer_ajustes(0, 10, 20)
    gestor.establecer_ajustes(2, -30, 40)
    gestor.bajar_fotografia(0)
    gestor.subir_fotografia(2)
    assert [f.ruta for f in gestor.obtener_fotografias()] == [rutas[1], rutas[2], rutas[0]]
    assert [gestor.obtener_ajustes(i) for i in range(3)] == [(0, 0), (-30, 40), (10, 20)]


def test_restablecer_no_altera_rotacion(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, 1)
    gestor.rotar_derecha(0)
    gestor.establecer_ajustes(0, 30, 15)
    assert gestor.restablecer_ajustes(0) == (0, 0)
    assert gestor.obtener_rotacion(0) == 90


def test_quitar_y_reagregar_reinicia_ajustes_y_rotacion(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, 1)
    gestor.establecer_ajustes(0, 40, -10)
    gestor.rotar_izquierda(0)
    gestor.quitar_fotografia(0)
    gestor.agregar_fotografia(rutas[0])
    assert gestor.obtener_ajustes(0) == (0, 0)
    assert gestor.obtener_rotacion(0) == 0


def test_vaciar_reinicia_todo(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, 1)
    gestor.establecer_ajustes(0, 15, 15)
    gestor.vaciar()
    assert gestor.cantidad() == 0
    assert rutas[0].exists()
    gestor.agregar_fotografia(rutas[0])
    assert gestor.obtener_ajustes(0) == (0, 0)


def test_indices_invalidos(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, 1)
    with pytest.raises(FotografiaNoEncontradaError):
        gestor.obtener_ajustes(5)
    with pytest.raises(FotografiaNoEncontradaError):
        gestor.restablecer_ajustes(-1)
    with pytest.raises(TypeError):
        gestor.establecer_ajustes(True, 0, 0)


def test_duplicado_no_modifica_ajustes(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, 1)
    gestor.establecer_ajustes(0, 22, 33)
    with pytest.raises(FotografiaDuplicadaError):
        gestor.agregar_fotografia(rutas[0])
    assert gestor.obtener_ajustes(0) == (22, 33)


def test_lote_invalido_no_altera_ajustes_previos(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, 1)
    gestor.establecer_ajustes(0, 7, 8)
    nueva = crear_imagen(tmp_path / 'nueva.png')
    with pytest.raises(FotografiaDuplicadaError):
        gestor.agregar_fotografias([nueva, rutas[0]])
    assert gestor.cantidad() == 1
    assert gestor.obtener_ajustes(0) == (7, 8)


def test_no_modificar_original(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, 1)
    antes = rutas[0].read_bytes()
    gestor.establecer_ajustes(0, -50, 90)
    gestor.restablecer_ajustes(0)
    assert rutas[0].read_bytes() == antes
