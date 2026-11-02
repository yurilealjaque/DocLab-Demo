"""Pruebas de integración de navegación de Digitalizar clases."""

import pytest
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QPushButton

import doclab.ui.main_window as modulo_ventana
from doclab.ui.main_window import VentanaPrincipal
from doclab.ui.pages.photos_to_pdf_page import PaginaFotosPDF


@pytest.fixture(scope="module")
def aplicacion():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def ventana(aplicacion):
    instancia = VentanaPrincipal()
    yield instancia
    instancia.close()


def test_pantalla_fotografias_registrada(ventana):
    assert isinstance(ventana.pagina_fotografias, PaginaFotosPDF)
    assert ventana.paginas.indexOf(ventana.pagina_fotografias) >= 0


def test_boton_lateral_abre_fotografias(ventana):
    ventana.boton_fotografias.click()
    assert ventana.paginas.currentWidget() is ventana.pagina_fotografias


def test_inicio_abre_fotografias(ventana):
    ventana.pagina_inicio.abrir_fotografias_pdf.emit()
    assert ventana.paginas.currentWidget() is ventana.pagina_fotografias


def test_estado_visual_boton_fotografias(ventana):
    ventana.navegar_a(ventana.pagina_fotografias)
    assert ventana.boton_fotografias.property("activo") is True
    assert ventana.boton_inicio.property("activo") is False


def test_inicio_contiene_tarjeta_habilitada(ventana):
    tarjeta = ventana.pagina_inicio.tarjeta_fotos
    assert tarjeta.isEnabled()
    botones = tarjeta.findChildren(QPushButton)
    assert len(botones) == 1
    assert botones[0].isEnabled()
    assert botones[0].text() == "Abrir herramienta"


def test_bloquea_cierre_durante_digitalizacion(ventana, monkeypatch):
    avisos = []
    monkeypatch.setattr(
        ventana.pagina_fotografias, "hay_operacion_activa", lambda: True
    )
    monkeypatch.setattr(
        modulo_ventana.QMessageBox,
        "warning",
        lambda *args: avisos.append(args),
    )
    evento = QCloseEvent()
    ventana.closeEvent(evento)
    assert not evento.isAccepted()
    assert len(avisos) == 1
    monkeypatch.setattr(
        ventana.pagina_fotografias, "hay_operacion_activa", lambda: False
    )


def test_permite_cierre_sin_operacion(ventana):
    assert not ventana.pagina_fotografias.hay_operacion_activa()
    evento = QCloseEvent()
    ventana.closeEvent(evento)
    assert evento.isAccepted()
