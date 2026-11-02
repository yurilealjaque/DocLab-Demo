"""Pruebas de rotación visual para la pantalla Imágenes a PDF."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from doclab.ui.pages.photos_to_pdf_page import PaginaFotosPDF


@pytest.fixture(scope="module")
def aplicacion():
    aplicacion = QApplication.instance()
    if aplicacion is None:
        aplicacion = QApplication([])
    return aplicacion


@pytest.fixture
def pagina(aplicacion):
    ventana = PaginaFotosPDF()
    yield ventana
    ventana.close()


def crear_imagen(ruta):
    imagen = QImage(120, 60, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.red)
    assert imagen.save(str(ruta), "PNG")
    return ruta


def test_controles_desactivados_si_no_hay_seleccion(pagina):
    assert not pagina.boton_rotar_izquierda.isEnabled()
    assert not pagina.boton_rotar_derecha.isEnabled()


def test_giro_derecha_actualiza_gestor_y_vista(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "foto.png")
    pagina.agregar_fotografias([ruta])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.boton_rotar_derecha.click()
    assert pagina.gestor.obtener_rotacion(0) == 90
    assert pagina.imagen_vista_previa.width() == 60
    assert pagina.imagen_vista_previa.height() == 120


def test_giro_izquierda_actualiza_gestor(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "foto.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.boton_rotar_izquierda.click()
    assert pagina.gestor.obtener_rotacion(0) == 270


def test_giro_completo_restaura_orientacion(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "foto.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    for _ in range(4):
        pagina.rotar_derecha()
    assert pagina.gestor.obtener_rotacion(0) == 0
    assert pagina.imagen_vista_previa.width() == 120
    assert pagina.imagen_vista_previa.height() == 60


def test_giro_permanece_con_la_imagen_al_reordenar(pagina, tmp_path):
    primera = crear_imagen(tmp_path / "uno.png")
    segunda = crear_imagen(tmp_path / "dos.png")
    pagina.agregar_fotografias([primera, segunda])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.rotar_derecha()
    pagina.bajar_fotografia()
    assert pagina.gestor.obtener_fotografias()[1].ruta == primera
    assert pagina.gestor.obtener_rotacion(1) == 90
    assert pagina.imagen_vista_previa.width() == 60


def test_quitar_ultima_imagen_desactiva_rotaciones(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "foto.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.quitar_fotografia()
    assert not pagina.boton_rotar_izquierda.isEnabled()
    assert not pagina.boton_rotar_derecha.isEnabled()
    assert pagina.imagen_vista_previa.isNull()


def test_giros_no_modifican_archivo_original(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "foto.png")
    contenido_original = ruta.read_bytes()
    pagina.agregar_fotografias([ruta])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.rotar_derecha()
    pagina.rotar_izquierda()
    assert ruta.read_bytes() == contenido_original
