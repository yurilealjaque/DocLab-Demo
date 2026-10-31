
"""
Pruebas del servicio de division PDF.
"""

import pytest

import doclab.services.pdf_split_service as modulo_servicio

from doclab.services.pdf_split_service import (
    ServicioDivisionPDF,
)


def test_servicio_extrae_rango(monkeypatch):
    servicio = ServicioDivisionPDF()
    llamadas = []

    def motor_simulado(
        origen,
        destino,
        inicio,
        fin
    ):
        llamadas.append(
            (origen, destino, inicio, fin)
        )
        return "resultado.pdf"

    monkeypatch.setattr(
        modulo_servicio,
        "extraer_rango_pdf",
        motor_simulado
    )

    resultado = servicio.extraer_rango(
        "original.pdf",
        "resultado.pdf",
        2,
        5
    )

    assert resultado == "resultado.pdf"
    assert llamadas == [
        ("original.pdf", "resultado.pdf", 2, 5)
    ]


def test_servicio_extrae_paginas(monkeypatch):
    servicio = ServicioDivisionPDF()
    llamadas = []

    def motor_simulado(
        origen,
        destino,
        paginas
    ):
        llamadas.append(
            (origen, destino, paginas)
        )
        return "seleccion.pdf"

    monkeypatch.setattr(
        modulo_servicio,
        "extraer_paginas_pdf",
        motor_simulado
    )

    resultado = servicio.extraer_paginas(
        "original.pdf",
        "seleccion.pdf",
        [1, 4, 8]
    )

    assert resultado == "seleccion.pdf"
    assert llamadas == [
        ("original.pdf", "seleccion.pdf", [1, 4, 8])
    ]


def test_servicio_separa_todas(monkeypatch):
    servicio = ServicioDivisionPDF()
    llamadas = []

    archivos_esperados = [
        "salida/pagina_001.pdf",
        "salida/pagina_002.pdf",
    ]

    def motor_simulado(origen, carpeta):
        llamadas.append(
            (origen, carpeta)
        )
        return archivos_esperados

    monkeypatch.setattr(
        modulo_servicio,
        "separar_paginas_pdf",
        motor_simulado
    )

    resultado = servicio.separar_todas(
        "original.pdf",
        "salida"
    )

    assert resultado == archivos_esperados
    assert llamadas == [
        ("original.pdf", "salida")
    ]


def test_servicio_propaga_errores(monkeypatch):
    servicio = ServicioDivisionPDF()

    def motor_con_error(*argumentos):
        raise ValueError(
            "Rango de paginas invalido"
        )

    monkeypatch.setattr(
        modulo_servicio,
        "extraer_rango_pdf",
        motor_con_error
    )

    with pytest.raises(
        ValueError,
        match="Rango de paginas invalido"
    ):
        servicio.extraer_rango(
            "original.pdf",
            "resultado.pdf",
            9,
            3
        )
