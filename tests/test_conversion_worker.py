"""Pruebas de señales del trabajador; invocan run() sin iniciar un hilo real."""

import pytest

import doclab.workers.conversion_worker as modulo_trabajador
from doclab.document_engine.pdf_validator import PDFCorruptoError, PDFProtegidoError
from doclab.workers.conversion_worker import TrabajadorConversion


@pytest.mark.parametrize(
    "error,fragmento_esperado",
    [
        (PDFProtegidoError("protegido"), "contrasena"),
        (PDFCorruptoError("corrupto"), "no es valido"),
    ],
)
def test_worker_emite_error_especifico(monkeypatch, error, fragmento_esperado):
    def simular_conversion(self, origen, destino):
        raise error

    monkeypatch.setattr(
        modulo_trabajador.ServicioConversion,
        "convertir",
        simular_conversion,
    )

    trabajador = TrabajadorConversion("entrada.pdf", "salida.docx")
    errores = []
    exitos = []
    trabajador.conversion_fallida.connect(errores.append)
    trabajador.conversion_exitosa.connect(exitos.append)

    trabajador.run()

    assert len(errores) == 1
    assert fragmento_esperado in errores[0]
    assert exitos == []


def test_worker_emite_exito(monkeypatch):
    def simular_conversion(self, origen, destino):
        return "salida.docx"

    monkeypatch.setattr(
        modulo_trabajador.ServicioConversion,
        "convertir",
        simular_conversion,
    )

    trabajador = TrabajadorConversion("entrada.pdf", "salida.docx")
    errores = []
    exitos = []
    trabajador.conversion_fallida.connect(errores.append)
    trabajador.conversion_exitosa.connect(exitos.append)

    trabajador.run()

    assert exitos == ["salida.docx"]
    assert errores == []


def test_worker_emite_error_generico_sin_filtrar_excepcion(monkeypatch):
    def simular_conversion(self, origen, destino):
        raise PermissionError("ruta privada /documentos/personales.pdf")

    monkeypatch.setattr(
        modulo_trabajador.ServicioConversion,
        "convertir",
        simular_conversion,
    )

    trabajador = TrabajadorConversion("entrada.pdf", "salida.docx")
    errores = []
    trabajador.conversion_fallida.connect(errores.append)

    trabajador.run()

    assert len(errores) == 1
    assert "No fue posible convertir" in errores[0]
    assert "personales.pdf" not in errores[0]
