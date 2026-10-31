
"""
Pruebas del trabajador de division PDF.
"""

import threading

import pytest

from PySide6.QtCore import QCoreApplication

from doclab.workers.pdf_split_worker import (
    TrabajadorDivisionPDF,
)

import doclab.workers.pdf_split_worker as modulo_worker


def test_worker_extrae_rango(monkeypatch):
    """
    Verifica la operacion por rango y
    la normalizacion del resultado.
    """

    class ServicioSimulado:
        def extraer_rango(
            self, origen, destino, inicio, fin
        ):
            assert origen == "original.pdf"
            assert destino == "salida.pdf"
            assert inicio == 2
            assert fin == 5

            return "salida.pdf"

    monkeypatch.setattr(
        modulo_worker,
        "ServicioDivisionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorDivisionPDF(
        modo="rango",
        ruta_origen="original.pdf",
        ruta_destino="salida.pdf",
        pagina_inicio=2,
        pagina_fin=5,
    )

    resultados = []
    trabajador.division_exitosa.connect(
        resultados.append
    )

    trabajador.run()

    assert resultados == [
        ["salida.pdf"]
    ]


def test_worker_extrae_paginas(monkeypatch):
    """
    Verifica la seleccion de paginas.
    """

    class ServicioSimulado:
        def extraer_paginas(
            self, origen, destino, paginas
        ):
            assert paginas == [1, 4, 8]
            return "seleccion.pdf"

    monkeypatch.setattr(
        modulo_worker,
        "ServicioDivisionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorDivisionPDF(
        modo="paginas",
        ruta_origen="original.pdf",
        ruta_destino="seleccion.pdf",
        paginas=[1, 4, 8],
    )

    resultados = []
    trabajador.division_exitosa.connect(
        resultados.append
    )

    trabajador.run()

    assert resultados == [
        ["seleccion.pdf"]
    ]


def test_worker_separa_todas(monkeypatch):
    """
    Verifica el retorno de multiples archivos.
    """

    class ServicioSimulado:
        def separar_todas(self, origen, carpeta):
            return [
                "salida/pagina_001.pdf",
                "salida/pagina_002.pdf",
            ]

    monkeypatch.setattr(
        modulo_worker,
        "ServicioDivisionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorDivisionPDF(
        modo="todas",
        ruta_origen="original.pdf",
        ruta_destino="salida",
    )

    resultados = []
    trabajador.division_exitosa.connect(
        resultados.append
    )

    trabajador.run()

    assert resultados == [[
        "salida/pagina_001.pdf",
        "salida/pagina_002.pdf",
    ]]


def test_worker_comunica_errores(monkeypatch):
    """
    Verifica que un error del servicio
    sea comunicado mediante una senal.
    """

    class ServicioSimulado:
        def extraer_rango(self, *argumentos):
            raise ValueError(
                "Rango invalido"
            )

    monkeypatch.setattr(
        modulo_worker,
        "ServicioDivisionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorDivisionPDF(
        modo="rango",
        ruta_origen="original.pdf",
        ruta_destino="salida.pdf",
        pagina_inicio=9,
        pagina_fin=3,
    )

    errores = []
    trabajador.division_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert errores == [
        "Rango invalido"
    ]


def test_worker_ejecuta_en_hilo_secundario(
    monkeypatch
):
    """
    Verifica que start() ejecuta realmente
    el servicio en un hilo secundario.
    """

    aplicacion = QCoreApplication.instance()

    if aplicacion is None:
        aplicacion = QCoreApplication([])

    hilo_principal = threading.get_ident()
    hilos_servicio = []

    class ServicioSimulado:
        def extraer_rango(self, *argumentos):
            hilos_servicio.append(
                threading.get_ident()
            )
            return "salida.pdf"

    monkeypatch.setattr(
        modulo_worker,
        "ServicioDivisionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorDivisionPDF(
        modo="rango",
        ruta_origen="original.pdf",
        ruta_destino="salida.pdf",
        pagina_inicio=1,
        pagina_fin=2,
    )

    trabajador.start()

    try:
        assert trabajador.wait(5000), (
            "El trabajador no termino "
            "dentro del tiempo de prueba."
        )
    finally:
        # Garantiza la finalizacion del hilo
        # antes de destruir el objeto.
        if trabajador.isRunning():
            trabajador.wait()

    assert len(hilos_servicio) == 1
    assert hilos_servicio[0] != hilo_principal
