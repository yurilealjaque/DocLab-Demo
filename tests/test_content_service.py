
import pytest

import doclab.services.conversion_service as modulo_servicio

from doclab.services.conversion_service import (
    ServicioConversion
)

from doclab.document_engine.pdf_content_detector import (
    ResultadoInspeccionPDF
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError
)


def test_servicio_inspecciona_pdf(monkeypatch):
    resultado_esperado = ResultadoInspeccionPDF(
        total_paginas=2,
        paginas_con_texto=(1,),
        paginas_sin_texto=(2,),
        clasificacion="mixto"
    )

    def simular_inspeccion(origen):
        assert origen == "documento.pdf"
        return resultado_esperado

    monkeypatch.setattr(
        modulo_servicio,
        "inspeccionar_contenido_pdf",
        simular_inspeccion
    )

    servicio = ServicioConversion()

    resultado = servicio.inspeccionar("documento.pdf")

    assert resultado == resultado_esperado


def test_servicio_propaga_error_pdf(monkeypatch):

    def simular_inspeccion(origen):
        raise PDFProtegidoError(
            "Documento protegido"
        )

    monkeypatch.setattr(
        modulo_servicio,
        "inspeccionar_contenido_pdf",
        simular_inspeccion
    )

    servicio = ServicioConversion()

    with pytest.raises(PDFProtegidoError):
        servicio.inspeccionar("protegido.pdf")
