
"""
Pruebas del trabajador de conversion OCR.

Comprueba la comunicacion mediante señales Qt
sin iniciar un hilo real en estas pruebas.
"""

from types import SimpleNamespace

import doclab.workers.ocr_conversion_worker as modulo

from doclab.workers.ocr_conversion_worker import (
    TrabajadorConversionOCR
)

from doclab.document_engine.ocr_engine import (
    RecursosOCRNoDisponiblesError
)


def test_trabajador_emite_conversion_exitosa(
    monkeypatch
):
    rutas_recibidas = []

    class ServicioSimulado:

        def convertir(self, origen, destino):

            assert origen == "entrada.pdf"
            assert destino == "salida.docx"

            return SimpleNamespace(
                ruta_destino="salida.docx",
                total_paginas=3,
                paginas_con_ocr=2,
                imagenes_exportadas=1
            )

    monkeypatch.setattr(
        modulo,
        "ServicioConversionOCR",
        ServicioSimulado
    )

    trabajador = TrabajadorConversionOCR(
        "entrada.pdf",
        "salida.docx"
    )

    trabajador.conversion_exitosa.connect(
        rutas_recibidas.append
    )

    trabajador.run()

    assert rutas_recibidas == [
        "salida.docx"
    ]


def test_trabajador_informa_recursos_faltantes(
    monkeypatch
):
    errores = []

    class ServicioSimulado:

        def convertir(self, origen, destino):
            raise RecursosOCRNoDisponiblesError(
                "Modelos no disponibles"
            )

    monkeypatch.setattr(
        modulo,
        "ServicioConversionOCR",
        ServicioSimulado
    )

    trabajador = TrabajadorConversionOCR(
        "entrada.pdf",
        "salida.docx"
    )

    trabajador.conversion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert len(errores) == 1

    assert "modelos de idioma" in errores[0]


def test_trabajador_informa_archivo_existente(
    monkeypatch
):
    errores = []

    class ServicioSimulado:

        def convertir(self, origen, destino):
            raise FileExistsError(
                "El archivo ya existe"
            )

    monkeypatch.setattr(
        modulo,
        "ServicioConversionOCR",
        ServicioSimulado
    )

    trabajador = TrabajadorConversionOCR(
        "entrada.pdf",
        "salida.docx"
    )

    trabajador.conversion_fallida.connect(
        errores.append
    )

    trabajador.run()

    assert len(errores) == 1
    assert "ya existe" in errores[0]
