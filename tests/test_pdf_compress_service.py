
"""
Pruebas unitarias del servicio de compresión PDF.

Se utiliza monkeypatch para aislar el servicio
del motor documental real.
"""

import pytest

import doclab.services.pdf_compress_service as modulo_servicio

from doclab.services.pdf_compress_service import (
    ServicioCompresionPDF,
)

from doclab.document_engine.pdf_compressor import (
    ResultadoCompresion,
    SinReduccionError,
)


def test_servicio_delega_al_motor(monkeypatch):
    """Comprueba que el servicio envía las rutas correctas."""

    llamadas = []

    resultado_esperado = ResultadoCompresion(
        ruta_destino="comprimido.pdf",
        tamano_original=10000,
        tamano_final=7000,
        paginas=3
    )

    def motor_simulado(ruta_origen, ruta_destino):
        llamadas.append((ruta_origen, ruta_destino))
        return resultado_esperado

    monkeypatch.setattr(
        modulo_servicio,
        "comprimir_pdf",
        motor_simulado
    )

    servicio = ServicioCompresionPDF()

    resultado = servicio.comprimir(
        "original.pdf",
        "comprimido.pdf"
    )

    assert llamadas == [
        ("original.pdf", "comprimido.pdf")
    ]

    assert resultado is resultado_esperado


def test_servicio_propaga_error_sin_reduccion(monkeypatch):
    """El servicio no debe ocultar la ausencia de ahorro."""

    def motor_simulado(ruta_origen, ruta_destino):
        raise SinReduccionError(
            "No se obtuvo una reducción de tamaño."
        )

    monkeypatch.setattr(
        modulo_servicio,
        "comprimir_pdf",
        motor_simulado
    )

    servicio = ServicioCompresionPDF()

    with pytest.raises(
        SinReduccionError,
        match="No se obtuvo una reducción"
    ):
        servicio.comprimir(
            "original.pdf",
            "comprimido.pdf"
        )


def test_servicio_propaga_error_destino_existente(
    monkeypatch
):
    """La protección contra sobrescritura se mantiene."""

    def motor_simulado(ruta_origen, ruta_destino):
        raise FileExistsError(
            "El destino ya existe."
        )

    monkeypatch.setattr(
        modulo_servicio,
        "comprimir_pdf",
        motor_simulado
    )

    servicio = ServicioCompresionPDF()

    with pytest.raises(FileExistsError):
        servicio.comprimir(
            "original.pdf",
            "comprimido.pdf"
        )
