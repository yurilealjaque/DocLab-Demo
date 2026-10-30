"""Pruebas del servicio que coordina la validación y la conversión."""

import pytest

import doclab.services.conversion_service as modulo_servicio
from doclab.document_engine.pdf_validator import PDFCorruptoError, PDFProtegidoError
from doclab.services.conversion_service import ServicioConversion


def test_valida_antes_de_convertir(monkeypatch):
    llamadas = []

    def simular_validacion(origen):
        llamadas.append(("validar", origen))
        return 1

    def simular_conversion(origen, destino):
        llamadas.append(("convertir", origen, destino))
        return destino

    monkeypatch.setattr(modulo_servicio, "validar_pdf", simular_validacion)
    monkeypatch.setattr(modulo_servicio, "convertir_pdf_a_word", simular_conversion)

    resultado = ServicioConversion().convertir("entrada.pdf", "salida.docx")

    assert resultado == "salida.docx"
    assert llamadas == [
        ("validar", "entrada.pdf"),
        ("convertir", "entrada.pdf", "salida.docx"),
    ]


@pytest.mark.parametrize("tipo_error", [PDFProtegidoError, PDFCorruptoError])
def test_no_convierte_cuando_falla_la_validacion(monkeypatch, tipo_error):
    conversion_ejecutada = False

    def simular_validacion(origen):
        raise tipo_error("Documento rechazado")

    def simular_conversion(origen, destino):
        nonlocal conversion_ejecutada
        conversion_ejecutada = True

    monkeypatch.setattr(modulo_servicio, "validar_pdf", simular_validacion)
    monkeypatch.setattr(modulo_servicio, "convertir_pdf_a_word", simular_conversion)

    with pytest.raises(tipo_error):
        ServicioConversion().convertir("entrada.pdf", "salida.docx")

    assert conversion_ejecutada is False
