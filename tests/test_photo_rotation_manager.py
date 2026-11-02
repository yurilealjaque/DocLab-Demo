"""Pruebas de rotación no destructiva en GestorFotografias."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine.photo_manager import (
    FotografiaNoEncontradaError,
    GestorFotografias,
)


def crear_imagen(ruta):
    imagen = QImage(80, 45, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.white)
    assert imagen.save(str(ruta), "PNG")
    return ruta


def test_rotacion_inicial_es_cero(tmp_path):
    gestor = GestorFotografias()
    gestor.agregar_fotografia(crear_imagen(tmp_path / "a.png"))
    assert gestor.obtener_rotacion(0) == 0


def test_girar_derecha_y_completar_vuelta(tmp_path):
    gestor = GestorFotografias()
    gestor.agregar_fotografia(crear_imagen(tmp_path / "a.png"))
    assert [gestor.rotar_derecha(0) for _ in range(4)] == [90, 180, 270, 0]


def test_girar_izquierda_y_regresar(tmp_path):
    gestor = GestorFotografias()
    gestor.agregar_fotografia(crear_imagen(tmp_path / "a.png"))
    assert gestor.rotar_izquierda(0) == 270
    assert gestor.rotar_derecha(0) == 0


def test_rotacion_pertenece_a_imagen_tras_reordenar(tmp_path):
    gestor = GestorFotografias()
    primera = crear_imagen(tmp_path / "primera.png")
    segunda = crear_imagen(tmp_path / "segunda.png")
    gestor.agregar_fotografias([primera, segunda])
    gestor.rotar_derecha(0)
    gestor.bajar_fotografia(0)
    assert gestor.obtener_fotografias()[1].ruta == primera
    assert gestor.obtener_rotacion(1) == 90
    assert gestor.obtener_rotacion(0) == 0


def test_quitar_y_reagregar_reinicia_rotacion(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_imagen(tmp_path / "a.png")
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)
    gestor.quitar_fotografia(0)
    gestor.agregar_fotografia(ruta)
    assert gestor.obtener_rotacion(0) == 0
    assert ruta.exists()


def test_vaciar_limpia_rotaciones(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_imagen(tmp_path / "a.png")
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)
    gestor.vaciar()
    gestor.agregar_fotografia(ruta)
    assert gestor.obtener_rotacion(0) == 0


def test_lote_invalido_no_cambia_rotaciones(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_imagen(tmp_path / "a.png")
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)
    with pytest.raises(FileNotFoundError):
        gestor.agregar_fotografias([tmp_path / "no_existe.png"])
    assert gestor.cantidad() == 1
    assert gestor.obtener_rotacion(0) == 90


def test_indices_invalidos_en_rotacion(tmp_path):
    gestor = GestorFotografias()
    gestor.agregar_fotografia(crear_imagen(tmp_path / "a.png"))
    with pytest.raises(TypeError):
        gestor.rotar_derecha(True)
    with pytest.raises(FotografiaNoEncontradaError):
        gestor.rotar_izquierda(4)
    with pytest.raises(FotografiaNoEncontradaError):
        gestor.obtener_rotacion(-1)


def test_rotacion_no_modifica_bytes_originales(tmp_path):
    ruta = crear_imagen(tmp_path / "a.png")
    contenido_original = ruta.read_bytes()
    gestor = GestorFotografias()
    gestor.agregar_fotografia(ruta)
    gestor.rotar_derecha(0)
    gestor.rotar_izquierda(0)
    assert ruta.read_bytes() == contenido_original
