"""Pruebas de miniaturas para la página Imágenes a PDF."""

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
    imagen = QImage(120, 90, QImage.Format.Format_RGB32)
    imagen.fill(QColor(color))
    assert imagen.save(str(ruta))
    return ruta


def test_miniatura_aparece_junto_al_nombre(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "foto.png", "red")
    pagina.agregar_fotografias([str(ruta)])

    elemento = pagina.lista_fotografias.item(0)
    assert elemento.text() == "1. foto.png"
    assert not elemento.icon().isNull()
    assert elemento.toolTip() == str(ruta)


def test_miniaturas_siguen_orden_de_archivos(pagina, tmp_path):
    primera = crear_imagen(tmp_path / "primera.png", "red")
    segunda = crear_imagen(tmp_path / "segunda.png", "blue")
    pagina.agregar_fotografias([str(primera), str(segunda)])

    pagina.lista_fotografias.setCurrentRow(1)
    pagina.subir_fotografia()

    assert pagina.lista_fotografias.item(0).text() == "1. segunda.png"
    assert pagina.lista_fotografias.item(1).text() == "2. primera.png"
    assert all(
        not pagina.lista_fotografias.item(i).icon().isNull()
        for i in range(2)
    )
    assert pagina.lista_fotografias.currentRow() == 0


def test_quitar_actualiza_miniaturas_y_contador(pagina, tmp_path):
    primera = crear_imagen(tmp_path / "uno.png", "red")
    segunda = crear_imagen(tmp_path / "dos.png", "blue")
    pagina.agregar_fotografias([str(primera), str(segunda)])

    pagina.lista_fotografias.setCurrentRow(0)
    pagina.quitar_fotografia()

    assert pagina.lista_fotografias.count() == 1
    assert pagina.lista_fotografias.item(0).text() == "1. dos.png"
    assert not pagina.lista_fotografias.item(0).icon().isNull()
    assert "1 imagen" in pagina.etiqueta_contador.text()


def test_imagen_desaparecida_no_interrumpe_lista(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "temporal.png", "red")
    pagina.agregar_fotografias([str(ruta)])
    ruta.unlink()

    pagina.actualizar_lista()

    assert pagina.lista_fotografias.count() == 1
    assert pagina.lista_fotografias.item(0).icon().isNull()
