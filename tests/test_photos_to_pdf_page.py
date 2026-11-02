
"""
Pruebas de la pantalla Digitalizar clases.

Verifica:
- Construccion de interfaz.
- Incorporacion y organizacion de fotografias.
- Proteccion de archivos originales.
- Bloqueo durante procesamiento.
- Señales y finalizacion del trabajador.
- Proteccion de cierre.
"""

import pytest

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QCloseEvent, QImage
from PySide6.QtWidgets import QApplication

import doclab.ui.pages.photos_to_pdf_page as modulo_pagina

from doclab.ui.pages.photos_to_pdf_page import (
    PaginaFotosPDF,
)

from doclab.document_engine.photos_to_pdf import (
    ResultadoFotosPDF,
)


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

    # Limpieza de las pruebas.
    ventana.trabajador = None
    ventana.close()


def crear_foto(ruta):
    imagen = QImage(
        100,
        80,
        QImage.Format.Format_RGB32,
    )
    imagen.fill(Qt.GlobalColor.white)

    assert imagen.save(str(ruta), "PNG")
    return ruta


def test_pantalla_inicial(pagina):
    assert pagina.gestor.cantidad() == 0
    assert pagina.trabajador is None
    assert not pagina.boton_generar.isEnabled()
    assert not pagina.boton_subir.isEnabled()
    assert pagina.progreso.isHidden()


def test_agregar_fotografias(pagina, tmp_path):
    rutas = [
        crear_foto(tmp_path / "foto_1.png"),
        crear_foto(tmp_path / "foto_2.png"),
    ]

    cantidad = pagina.agregar_fotografias(rutas)

    assert cantidad == 2
    assert pagina.gestor.cantidad() == 2
    assert pagina.lista_fotografias.count() == 2
    assert pagina.boton_generar.isEnabled()


def test_reordenar_fotografias(pagina, tmp_path):
    rutas = [
        crear_foto(tmp_path / "foto_1.png"),
        crear_foto(tmp_path / "foto_2.png"),
    ]

    pagina.agregar_fotografias(rutas)

    pagina.lista_fotografias.setCurrentRow(1)
    pagina.subir_fotografia()

    fotografias = pagina.gestor.obtener_fotografias()

    assert fotografias[0].ruta == rutas[1]
    assert fotografias[1].ruta == rutas[0]
    assert pagina.lista_fotografias.currentRow() == 0

    pagina.bajar_fotografia()

    fotografias = pagina.gestor.obtener_fotografias()

    assert fotografias[0].ruta == rutas[0]
    assert fotografias[1].ruta == rutas[1]


def test_quitar_no_borra_original(pagina, tmp_path):
    ruta = crear_foto(tmp_path / "original.png")

    pagina.agregar_fotografias([ruta])
    pagina.lista_fotografias.setCurrentRow(0)
    pagina.quitar_fotografia()

    assert pagina.gestor.cantidad() == 0
    assert ruta.exists()
    assert not pagina.boton_generar.isEnabled()


def test_lote_invalido_no_modifica_lista(
    pagina,
    tmp_path,
):
    ruta = crear_foto(tmp_path / "correcta.png")
    inexistente = tmp_path / "inexistente.png"

    with pytest.raises(FileNotFoundError):
        pagina.agregar_fotografias([
            ruta,
            inexistente,
        ])

    assert pagina.gestor.cantidad() == 0
    assert pagina.lista_fotografias.count() == 0


class TrabajadorSimulado(QObject):
    generacion_exitosa = Signal(object)
    generacion_fallida = Signal(str)
    finished = Signal()

    def __init__(self, gestor, destino, parent=None):
        super().__init__(parent)
        self.gestor = gestor
        self.destino = destino
        self.iniciado = False

    def start(self):
        self.iniciado = True

    def isRunning(self):
        return self.iniciado


def test_trabajador_bloquea_controles(
    pagina,
    tmp_path,
    monkeypatch,
):
    ruta = crear_foto(tmp_path / "foto.png")
    pagina.agregar_fotografias([ruta])

    monkeypatch.setattr(
        modulo_pagina,
        "TrabajadorFotosPDF",
        TrabajadorSimulado,
    )

    pagina.iniciar_generacion(
        tmp_path / "resultado.pdf"
    )

    assert pagina.trabajador.iniciado
    assert not pagina.boton_agregar.isEnabled()
    assert not pagina.boton_generar.isEnabled()
    assert not pagina.lista_fotografias.isEnabled()
    assert not pagina.progreso.isHidden()

    trabajador = pagina.trabajador
    trabajador.iniciado = False
    trabajador.finished.emit()

    assert pagina.trabajador is None
    assert pagina.boton_agregar.isEnabled()
    assert pagina.boton_generar.isEnabled()
    assert pagina.progreso.isHidden()


def test_resultado_del_trabajador(
    pagina,
    tmp_path,
    monkeypatch,
):
    ruta = crear_foto(tmp_path / "foto.png")
    pagina.agregar_fotografias([ruta])

    monkeypatch.setattr(
        modulo_pagina,
        "TrabajadorFotosPDF",
        TrabajadorSimulado,
    )

    mensajes = []

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "information",
        lambda *args: mensajes.append(args),
    )

    pagina.iniciar_generacion(
        tmp_path / "resultado.pdf"
    )

    trabajador = pagina.trabajador

    resultado = ResultadoFotosPDF(
        ruta_destino=tmp_path / "resultado.pdf",
        numero_paginas=1,
        tamano_bytes=5000,
    )

    trabajador.generacion_exitosa.emit(resultado)

    assert len(mensajes) == 1
    assert "correctamente" in pagina.etiqueta_estado.text()

    trabajador.iniciado = False
    trabajador.finished.emit()

    assert pagina.trabajador is None


def test_impide_cierre_durante_procesamiento(
    pagina,
    tmp_path,
    monkeypatch,
):
    ruta = crear_foto(tmp_path / "foto.png")
    pagina.agregar_fotografias([ruta])

    monkeypatch.setattr(
        modulo_pagina,
        "TrabajadorFotosPDF",
        TrabajadorSimulado,
    )

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "warning",
        lambda *args: None,
    )

    pagina.iniciar_generacion(
        tmp_path / "resultado.pdf"
    )

    evento = QCloseEvent()
    pagina.closeEvent(evento)

    assert not evento.isAccepted()

    trabajador = pagina.trabajador
    trabajador.iniciado = False
    trabajador.finished.emit()
