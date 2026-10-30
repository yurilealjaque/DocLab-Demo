
import pytest

import doclab.workers.conversion_worker as modulo_worker

from doclab.workers.conversion_worker import (
    TrabajadorInspeccion
)

from doclab.document_engine.pdf_content_detector import (
    ResultadoInspeccionPDF
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError
)


def test_inspeccion_exitosa(monkeypatch):

    resultado_esperado = ResultadoInspeccionPDF(
        total_paginas=3,
        paginas_con_texto=(1, 3),
        paginas_sin_texto=(2,),
        clasificacion="mixto"
    )

    class ServicioSimulado:

        def inspeccionar(self, origen):
            assert origen == "documento.pdf"
            return resultado_esperado

    monkeypatch.setattr(
        modulo_worker,
        "ServicioConversion",
        ServicioSimulado
    )

    trabajador = TrabajadorInspeccion("documento.pdf")

    resultados = []

    trabajador.inspeccion_exitosa.connect(
        resultados.append
    )

    trabajador.run()

    assert resultados == [resultado_esperado]


@pytest.mark.parametrize(
    "tipo_error, texto_esperado",
    [
        (PDFProtegidoError, "contrasena"),
        (PDFCorruptoError, "no es valido"),
    ]
)
def test_inspeccion_error_especifico(
    monkeypatch,
    tipo_error,
    texto_esperado
):

    class ServicioSimulado:

        def inspeccionar(self, origen):
            raise tipo_error("Error simulado")

    monkeypatch.setattr(
        modulo_worker,
        "ServicioConversion",
        ServicioSimulado
    )

    trabajador = TrabajadorInspeccion("documento.pdf")

    mensajes = []

    trabajador.inspeccion_fallida.connect(
        mensajes.append
    )

    trabajador.run()

    assert len(mensajes) == 1
    assert texto_esperado in mensajes[0]


def test_inspeccion_error_inesperado(monkeypatch):

    class ServicioSimulado:

        def inspeccionar(self, origen):
            raise RuntimeError(
                "Error interno reservado"
            )

    monkeypatch.setattr(
        modulo_worker,
        "ServicioConversion",
        ServicioSimulado
    )

    trabajador = TrabajadorInspeccion("documento.pdf")

    mensajes = []

    trabajador.inspeccion_fallida.connect(
        mensajes.append
    )

    trabajador.run()

    assert len(mensajes) == 1
    assert "No fue posible analizar" in mensajes[0]

    # No filtrar errores internos al usuario.
    assert "Error interno reservado" not in mensajes[0]
