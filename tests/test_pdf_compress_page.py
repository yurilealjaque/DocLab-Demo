
"""
Pruebas automatizadas de la pantalla Comprimir PDF.

Cobertura:
- Construcción de interfaz.
- Estado inicial.
- Carga de PDF válido.
- Rechazo de PDF inválido.
- Bloqueo de controles durante procesamiento.
- Protección de archivos existentes.
- Protección del documento original.
- Presentación de resultados.
- Manejo de errores.
- Señales simuladas de QThread.
- Protección de cierre.

Las pruebas no modifican documentos personales.
"""

import pymupdf
import pytest

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMessageBox

import doclab.ui.pages.pdf_compress_page as modulo_pagina

from doclab.ui.pages.pdf_compress_page import (
    PaginaCompresionPDF,
)

from doclab.document_engine.pdf_compressor import (
    ResultadoCompresion,
)


# ---------------------------------------
# 1. PREPARACIÓN DE PRUEBAS
# ---------------------------------------

@pytest.fixture(scope="module")
def aplicacion():
    """Crea o reutiliza la aplicación Qt."""

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@pytest.fixture
def pagina(aplicacion):
    """Entrega una pantalla nueva para cada prueba."""

    ventana = PaginaCompresionPDF()

    yield ventana

    # Evitar diálogos durante la limpieza.
    ventana.trabajador = None
    ventana.close()


def crear_pdf(ruta, cantidad_paginas=2):
    """Genera un PDF temporal con texto."""

    with pymupdf.open() as documento:
        for numero in range(cantidad_paginas):
            hoja = documento.new_page()
            hoja.insert_text(
                (72, 72),
                f"Contenido de prueba {numero + 1}"
            )

        documento.save(str(ruta))


def crear_resultado():
    """Construye un resultado simulado de compresión."""

    return ResultadoCompresion(
        ruta_destino="resultado.pdf",
        tamano_original=10000,
        tamano_final=6000,
        paginas=2
    )


class TrabajadorSimulado(QObject):
    """
    Simula las señales Qt sin ejecutar
    el motor real ni crear un hilo.
    """

    compresion_exitosa = Signal(object)
    compresion_fallida = Signal(str)
    finished = Signal()

    def __init__(self, ruta_origen, ruta_destino, parent=None):
        super().__init__(parent)

        self.ruta_origen = ruta_origen
        self.ruta_destino = ruta_destino
        self.iniciado = False

    def start(self):
        self.iniciado = True

    def isRunning(self):
        return self.iniciado


# ---------------------------------------
# 2. ESTADO INICIAL
# ---------------------------------------

def test_pantalla_se_construye(pagina):
    """Comprueba la creación de componentes básicos."""

    assert pagina is not None
    assert pagina.boton_seleccionar is not None
    assert pagina.boton_comprimir is not None
    assert pagina.progreso is not None
    assert pagina.etiqueta_estado is not None


def test_estado_inicial(pagina):
    """No debe permitirse comprimir sin origen."""

    assert pagina.ruta_pdf is None
    assert pagina.trabajador is None
    assert not pagina.boton_comprimir.isEnabled()
    assert not pagina.progreso.isVisible()


# ---------------------------------------
# 3. CARGA DE DOCUMENTOS
# ---------------------------------------

def test_cargar_pdf_valido(pagina, tmp_path):
    """Comprueba los datos mostrados tras cargar."""

    origen = tmp_path / "clase.pdf"
    crear_pdf(origen, cantidad_paginas=3)

    pagina.cargar_pdf(origen)

    assert pagina.ruta_pdf == str(origen)
    assert pagina.boton_comprimir.isEnabled()
    assert "clase.pdf" in pagina.etiqueta_archivo.text()
    assert "3 página(s)" in pagina.etiqueta_resumen.text()


def test_rechaza_pdf_inexistente(pagina, tmp_path):
    """No debe aceptar un documento inexistente."""

    origen = tmp_path / "inexistente.pdf"

    with pytest.raises(FileNotFoundError):
        pagina.cargar_pdf(origen)

    assert pagina.ruta_pdf is None
    assert not pagina.boton_comprimir.isEnabled()


def test_rechaza_pdf_corrupto(pagina, tmp_path):
    """No debe aceptar un archivo PDF ilegible."""

    origen = tmp_path / "corrupto.pdf"

    origen.write_text(
        "No es un documento PDF",
        encoding="utf-8"
    )

    with pytest.raises(Exception):
        pagina.cargar_pdf(origen)

    assert pagina.ruta_pdf is None
    assert not pagina.boton_comprimir.isEnabled()


# ---------------------------------------
# 4. ESTADO DE PROCESAMIENTO
# ---------------------------------------

def test_bloquea_controles_durante_compresion(
    pagina,
    tmp_path
):
    """Impide cambiar documentos durante la operación."""

    origen = tmp_path / "original.pdf"
    crear_pdf(origen)

    pagina.cargar_pdf(origen)

    pagina.cambiar_estado_procesamiento(True)

    assert not pagina.boton_seleccionar.isEnabled()
    assert not pagina.boton_comprimir.isEnabled()
    assert pagina.progreso.isHidden() is False


def test_restaura_controles_tras_compresion(
    pagina,
    tmp_path
):
    """Recupera los controles al finalizar."""

    origen = tmp_path / "original.pdf"
    crear_pdf(origen)

    pagina.cargar_pdf(origen)
    pagina.cambiar_estado_procesamiento(True)
    pagina.cambiar_estado_procesamiento(False)

    assert pagina.boton_seleccionar.isEnabled()
    assert pagina.boton_comprimir.isEnabled()
    assert pagina.progreso.isHidden()


# ---------------------------------------
# 5. PROTECCIÓN DE DESTINOS
# ---------------------------------------

def test_no_sobrescribe_destino_existente(
    pagina,
    tmp_path,
    monkeypatch
):
    """No debe iniciar el trabajador si existe salida."""

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "existente.pdf"

    crear_pdf(origen)
    crear_pdf(destino)

    pagina.cargar_pdf(origen)

    avisos = []
    inicios = []

    monkeypatch.setattr(
        modulo_pagina.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(destino), "")
    )

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "warning",
        lambda *args: avisos.append(args)
    )

    monkeypatch.setattr(
        pagina,
        "iniciar_compresion",
        lambda ruta: inicios.append(ruta)
    )

    pagina.solicitar_compresion()

    assert len(avisos) == 1
    assert inicios == []
    assert destino.is_file()


def test_no_permite_sobrescribir_original(
    pagina,
    tmp_path,
    monkeypatch
):
    """No debe reemplazar el archivo de entrada."""

    origen = tmp_path / "original.pdf"
    crear_pdf(origen)

    pagina.cargar_pdf(origen)

    avisos = []
    inicios = []

    monkeypatch.setattr(
        modulo_pagina.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(origen), "")
    )

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "warning",
        lambda *args: avisos.append(args)
    )

    monkeypatch.setattr(
        pagina,
        "iniciar_compresion",
        lambda ruta: inicios.append(ruta)
    )

    pagina.solicitar_compresion()

    assert len(avisos) == 1
    assert inicios == []


# ---------------------------------------
# 6. PRESENTACIÓN DE RESULTADOS
# ---------------------------------------

def test_muestra_resultado_correctamente(
    pagina,
    monkeypatch
):
    """Comprueba los datos de ahorro informados."""

    mensajes = []

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "information",
        lambda *args: mensajes.append(args)
    )

    resultado = crear_resultado()

    pagina.mostrar_resultado(resultado)

    assert len(mensajes) == 1
    assert "40.00%" in mensajes[0][2]
    assert "40.00%" in pagina.etiqueta_estado.text()


def test_muestra_error_comprensible(
    pagina,
    monkeypatch
):
    """Comprueba la presentación de errores."""

    avisos = []

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "warning",
        lambda *args: avisos.append(args)
    )

    pagina.mostrar_error(
        "No se obtuvo una reducción del tamaño."
    )

    assert len(avisos) == 1
    assert "No se obtuvo" in pagina.etiqueta_estado.text()


# ---------------------------------------
# 7. INTEGRACIÓN SIMULADA CON TRABAJADOR
# ---------------------------------------

def test_inicia_trabajador_y_recibe_resultado(
    pagina,
    tmp_path,
    monkeypatch
):
    """
    Comprueba las conexiones de señales sin
    ejecutar el servicio ni un hilo real.
    """

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen)
    pagina.cargar_pdf(origen)

    mensajes = []

    monkeypatch.setattr(
        modulo_pagina,
        "TrabajadorCompresionPDF",
        TrabajadorSimulado
    )

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "information",
        lambda *args: mensajes.append(args)
    )

    pagina.iniciar_compresion(str(destino))

    trabajador = pagina.trabajador

    assert trabajador is not None
    assert trabajador.iniciado
    assert trabajador.ruta_origen == str(origen)
    assert trabajador.ruta_destino == str(destino)
    assert not pagina.boton_comprimir.isEnabled()

    trabajador.compresion_exitosa.emit(
        crear_resultado()
    )

    assert len(mensajes) == 1

    # Simular la finalización del trabajador.
    trabajador.iniciado = False
    trabajador.finished.emit()

    assert pagina.trabajador is None
    assert pagina.boton_comprimir.isEnabled()


# ---------------------------------------
# 8. PROTECCIÓN DE CIERRE
# ---------------------------------------

def test_impide_cierre_durante_operacion(
    pagina,
    monkeypatch
):
    """El cierre se rechaza mientras hay trabajador."""

    avisos = []

    monkeypatch.setattr(
        modulo_pagina.QMessageBox,
        "warning",
        lambda *args: avisos.append(args)
    )

    pagina.trabajador = TrabajadorSimulado(
        "origen.pdf",
        "resultado.pdf"
    )

    pagina.trabajador.start()

    evento = QCloseEvent()

    pagina.closeEvent(evento)

    assert not evento.isAccepted()
    assert len(avisos) == 1

    pagina.trabajador = None
