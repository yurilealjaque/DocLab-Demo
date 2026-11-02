
"""
Pruebas del trabajador de Fotografias a PDF.
"""

import threading

import pytest

from PySide6.QtCore import QCoreApplication

import doclab.workers.photos_to_pdf_worker as modulo_trabajador

from doclab.workers.photos_to_pdf_worker import (
    TrabajadorFotosPDF,
)

from doclab.document_engine.photo_manager import (
    GestorFotografias,
)

from doclab.document_engine.photos_to_pdf import (
    ResultadoFotosPDF,
    ErrorFotosPDF,
)

from doclab.document_engine.image_validator import (
    ImagenCorruptaError,
    ImagenDemasiadoGrandeError,
)


@pytest.fixture(scope="module")
def aplicacion_qt():
    """Proporciona la aplicacion Qt necesaria."""

    aplicacion = QCoreApplication.instance()

    if aplicacion is None:
        aplicacion = QCoreApplication([])

    return aplicacion


def preparar_trabajador(monkeypatch, error=None):
    """Prepara un trabajador con servicio simulado."""

    resultado = ResultadoFotosPDF(
        ruta_destino="resultado.pdf",
        numero_paginas=2,
        tamano_bytes=5000,
    )

    class ServicioSimulado:
        def generar(self, gestor, ruta_destino):
            if error is not None:
                raise error
            return resultado

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioFotosPDF",
        ServicioSimulado,
    )

    trabajador = TrabajadorFotosPDF(
        GestorFotografias(),
        "resultado.pdf",
    )

    return trabajador, resultado


def test_trabajador_emite_resultado_exitoso(
    monkeypatch,
    aplicacion_qt,
):
    trabajador, esperado = preparar_trabajador(
        monkeypatch
    )

    resultados = []
    errores = []

    trabajador.generacion_exitosa.connect(
        resultados.append
    )
    trabajador.generacion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert resultados == [esperado]
    assert errores == []


@pytest.mark.parametrize(
    "error, texto_esperado",
    [
        (
            ImagenDemasiadoGrandeError("Grande"),
            "límites",
        ),
        (
            ImagenCorruptaError("Corrupta"),
            "dañada",
        ),
        (
            FileExistsError("Existe"),
            "Ya existe",
        ),
        (
            FileNotFoundError("No existe"),
            "No se encontró",
        ),
        (
            ValueError("Solicitud inválida"),
            "Comprueba",
        ),
        (
            ErrorFotosPDF("Error del motor"),
            "No fue posible",
        ),
        (
            OSError("Sin permisos"),
            "guardar",
        ),
        (
            RuntimeError("Error inesperado"),
            "inesperado",
        ),
    ],
)
def test_trabajador_informa_errores(
    monkeypatch,
    aplicacion_qt,
    error,
    texto_esperado,
):
    trabajador, _ = preparar_trabajador(
        monkeypatch,
        error=error,
    )

    resultados = []
    errores = []

    trabajador.generacion_exitosa.connect(
        resultados.append
    )
    trabajador.generacion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert resultados == []
    assert len(errores) == 1
    assert texto_esperado.lower() in errores[0].lower()


def test_trabajador_ejecuta_servicio_en_hilo_secundario(
    monkeypatch,
    aplicacion_qt,
):
    """
    Verifica que start() ejecuta el servicio
    fuera del hilo principal.
    """

    hilo_principal = threading.get_ident()
    hilos_utilizados = []

    resultado_esperado = ResultadoFotosPDF(
        ruta_destino="resultado.pdf",
        numero_paginas=1,
        tamano_bytes=2000,
    )

    class ServicioSimulado:
        def generar(self, gestor, ruta_destino):
            hilos_utilizados.append(
                threading.get_ident()
            )
            return resultado_esperado

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioFotosPDF",
        ServicioSimulado,
    )

    trabajador = TrabajadorFotosPDF(
        GestorFotografias(),
        "resultado.pdf",
    )

    trabajador.start()

    try:
        assert trabajador.wait(5000)

        assert hilos_utilizados
        assert hilos_utilizados[0] != hilo_principal

    finally:
        if trabajador.isRunning():
            trabajador.wait()


def test_trabajador_conserva_parametros(
    aplicacion_qt,
):
    """Comprueba que guarda el gestor y el destino."""

    gestor = GestorFotografias()
    destino = "mi_documento.pdf"

    trabajador = TrabajadorFotosPDF(
        gestor,
        destino,
    )

    assert trabajador.gestor is gestor
    assert trabajador.ruta_destino == destino
