"""Pruebas del incremento 9C: brillo y contraste en la interfaz."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
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
    vista = PaginaFotosPDF()
    yield vista
    vista.close()


def crear_imagen(ruta):
    imagen = QImage(120, 60, QImage.Format.Format_RGB32)
    imagen.fill(Qt.GlobalColor.gray)
    assert imagen.save(str(ruta), "PNG")
    return ruta


def test_deslizadores_desactivados_sin_imagen(pagina):
    assert not pagina.deslizador_brillo.isEnabled()
    assert not pagina.deslizador_contraste.isEnabled()
    assert not pagina.boton_restablecer_ajustes.isEnabled()


def test_ajustes_se_guardan_y_aparecen_en_etiquetas(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "uno.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.deslizador_brillo.setValue(30)
    pagina.deslizador_contraste.setValue(-15)
    assert pagina.gestor.obtener_ajustes(0) == (30, -15)
    assert pagina.etiqueta_brillo.text() == "Brillo: +30"
    assert pagina.etiqueta_contraste.text() == "Contraste: -15"


def test_previsualizacion_reacciona_al_brillo(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "uno.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    anterior = pagina.imagen_vista_previa.pixelColor(10, 10)
    pagina.deslizador_brillo.setValue(40)
    posterior = pagina.imagen_vista_previa.pixelColor(10, 10)
    assert posterior.red() > anterior.red()
    assert pagina.imagen_vista_previa.size() == pagina.imagen_base_vista_previa.size()


def test_ajustes_son_individuales_y_se_recuperan(pagina, tmp_path):
    rutas = [crear_imagen(tmp_path / "uno.png"), crear_imagen(tmp_path / "dos.png")]
    pagina.agregar_fotografias(rutas)
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.deslizador_brillo.setValue(45)
    pagina.lista_fotografias.setCurrentRow(1)
    assert pagina.deslizador_brillo.value() == 0
    pagina.deslizador_contraste.setValue(25)
    pagina.lista_fotografias.setCurrentRow(0)
    assert pagina.deslizador_brillo.value() == 45
    assert pagina.deslizador_contraste.value() == 0
    assert pagina.gestor.obtener_ajustes(1) == (0, 25)


def test_restablecer_conserva_rotacion(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "uno.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.rotar_derecha()
    pagina.deslizador_brillo.setValue(45)
    pagina.boton_restablecer_ajustes.click()
    assert pagina.gestor.obtener_ajustes(0) == (0, 0)
    assert pagina.gestor.obtener_rotacion(0) == 90
    assert pagina.deslizador_brillo.value() == 0
    assert pagina.imagen_vista_previa.width() == 60


def test_ajustes_acompanan_la_imagen_al_reordenar(pagina, tmp_path):
    primera = crear_imagen(tmp_path / "uno.png")
    segunda = crear_imagen(tmp_path / "dos.png")
    pagina.agregar_fotografias([primera, segunda])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.deslizador_brillo.setValue(50)
    pagina.bajar_fotografia()
    assert pagina.gestor.obtener_fotografias()[1].ruta == primera
    assert pagina.gestor.obtener_ajustes(1) == (50, 0)
    assert pagina.deslizador_brillo.value() == 50


def test_ajustes_no_modifican_archivo_original(pagina, tmp_path):
    ruta = crear_imagen(tmp_path / "uno.png")
    original = ruta.read_bytes()
    pagina.agregar_fotografias([ruta])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.deslizador_brillo.setValue(95)
    pagina.deslizador_contraste.setValue(90)
    pagina.actualizar_miniatura_seleccionada()
    assert ruta.read_bytes() == original


def test_quitar_ultima_imagen_reinicia_controles(pagina, tmp_path):
    pagina.agregar_fotografias([crear_imagen(tmp_path / "uno.png")])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.deslizador_brillo.setValue(20)
    pagina.quitar_fotografia()
    assert pagina.deslizador_brillo.value() == 0
    assert not pagina.deslizador_brillo.isEnabled()
    assert pagina.imagen_vista_previa.isNull()
