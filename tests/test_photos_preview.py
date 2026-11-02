"""Pruebas de previsualización ampliada en Imágenes a PDF."""

import pytest
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from doclab.ui.pages.photos_to_pdf_page import PaginaFotosPDF


@pytest.fixture(scope="module")
def aplicacion():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def pagina(aplicacion):
    ventana = PaginaFotosPDF()
    yield ventana
    ventana.close()


def crear_imagen(ruta, color):
    imagen = QImage(240, 120, QImage.Format.Format_RGB32)
    imagen.fill(QColor(color))
    assert imagen.save(str(ruta))
    return ruta


def test_sin_seleccion_muestra_instruccion(pagina):
    assert pagina.etiqueta_vista_previa.pixmap().isNull()
    assert "Selecciona" in pagina.etiqueta_vista_previa.text()


def test_seleccion_muestra_imagen_y_nombre(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "roja.png", "red")
    pagina.agregar_fotografias([str(ruta)])
    pagina.lista_fotografias.setCurrentRow(0)
    assert not pagina.etiqueta_vista_previa.pixmap().isNull()
    assert pagina.etiqueta_nombre_vista_previa.text() == "roja.png"


def test_cambio_de_seleccion_actualiza_vista(pagina, tmp_path):
    roja = crear_imagen(tmp_path / "roja.png", "red")
    azul = crear_imagen(tmp_path / "azul.png", "blue")
    pagina.agregar_fotografias([str(roja), str(azul)])

    pagina.lista_fotografias.setCurrentRow(0)
    assert pagina.imagen_vista_previa.pixelColor(0, 0) == QColor("red")

    pagina.lista_fotografias.setCurrentRow(1)
    assert pagina.imagen_vista_previa.pixelColor(0, 0) == QColor("blue")
    assert pagina.etiqueta_nombre_vista_previa.text() == "azul.png"


def test_quitar_actualiza_panel(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "unica.png", "red")
    pagina.agregar_fotografias([str(ruta)])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.quitar_fotografia()

    assert pagina.lista_fotografias.count() == 0
    assert pagina.etiqueta_vista_previa.pixmap().isNull()
    assert "Selecciona" in pagina.etiqueta_vista_previa.text()


def test_archivo_ausente_muestra_mensaje(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "temporal.png", "red")
    pagina.agregar_fotografias([str(ruta)])
    ruta.unlink()
    pagina.lista_fotografias.setCurrentRow(0)

    assert pagina.etiqueta_vista_previa.pixmap().isNull()
    assert "No se pudo" in pagina.etiqueta_vista_previa.text()
