
"""
Pruebas del trabajador de compresión PDF.
"""

import threading

import pytest

from PySide6.QtCore import QCoreApplication

import doclab.workers.pdf_compress_worker as modulo_trabajador

from doclab.workers.pdf_compress_worker import (
    TrabajadorCompresionPDF,
)

from doclab.document_engine.pdf_compressor import (
    ResultadoCompresion,
    SinReduccionError,
    DocumentoFirmadoError,
)


@pytest.fixture(scope="module")
def aplicacion_qt():
    """Proporciona la aplicación Qt necesaria."""

    aplicacion = QCoreApplication.instance()

    if aplicacion is None:
        aplicacion = QCoreApplication([])

    return aplicacion


def test_trabajador_emite_resultado_exitoso(
    monkeypatch,
    aplicacion_qt
):
    """Comprueba la señal con las estadísticas."""

    resultado_esperado = ResultadoCompresion(
        ruta_destino="salida.pdf",
        tamano_original=10000,
        tamano_final=6000,
        paginas=2
    )

    class ServicioSimulado:
        def comprimir(self, ruta_origen, ruta_destino):
            return resultado_esperado

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioCompresionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorCompresionPDF(
        "origen.pdf",
        "salida.pdf"
    )

    resultados = []
    errores = []

    trabajador.compresion_exitosa.connect(
        resultados.append
    )
    trabajador.compresion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert resultados == [resultado_esperado]
    assert errores == []


def test_trabajador_informa_sin_reduccion(
    monkeypatch,
    aplicacion_qt
):
    """Comprueba el mensaje cuando no existe ahorro."""

    class ServicioSimulado:
        def comprimir(self, ruta_origen, ruta_destino):
            raise SinReduccionError(
                "Sin reducción"
            )

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioCompresionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorCompresionPDF(
        "origen.pdf",
        "salida.pdf"
    )

    errores = []
    trabajador.compresion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert len(errores) == 1
    assert "No se obtuvo una reducción" in errores[0]


def test_trabajador_rechaza_documento_firmado(
    monkeypatch,
    aplicacion_qt
):
    """Comprueba el rechazo preventivo de firmas."""

    class ServicioSimulado:
        def comprimir(self, ruta_origen, ruta_destino):
            raise DocumentoFirmadoError(
                "Posible firma"
            )

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioCompresionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorCompresionPDF(
        "origen.pdf",
        "salida.pdf"
    )

    errores = []
    trabajador.compresion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert len(errores) == 1
    assert "firma" in errores[0].lower()


def test_trabajador_se_ejecuta_en_hilo_secundario(
    monkeypatch,
    aplicacion_qt
):
    """Comprueba que start() no ejecuta el servicio en el hilo principal."""

    hilo_principal = threading.get_ident()
    hilos_ejecucion = []

    resultado_esperado = ResultadoCompresion(
        ruta_destino="salida.pdf",
        tamano_original=10000,
        tamano_final=5000,
        paginas=1
    )

    class ServicioSimulado:
        def comprimir(self, ruta_origen, ruta_destino):
            hilos_ejecucion.append(
                threading.get_ident()
            )
            return resultado_esperado

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioCompresionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorCompresionPDF(
        "origen.pdf",
        "salida.pdf"
    )

    trabajador.start()

    try:
        assert trabajador.wait(5000)
        assert hilos_ejecucion
        assert hilos_ejecucion[0] != hilo_principal

    finally:
        if trabajador.isRunning():
            trabajador.wait()
