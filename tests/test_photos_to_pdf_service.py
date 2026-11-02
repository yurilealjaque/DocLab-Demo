
"""
Pruebas del servicio Fotografías a PDF.

Se utilizan motores simulados para comprobar
la delegación y propagación de excepciones.

También se incluye una prueba de integración real.
"""

import pytest
import pymupdf

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

import doclab.services.photos_to_pdf_service as modulo_servicio

from doclab.services.photos_to_pdf_service import (
    ServicioFotosPDF,
)

from doclab.document_engine.photo_manager import (
    GestorFotografias,
)

from doclab.document_engine.photos_to_pdf import (
    ResultadoFotosPDF,
    ErrorFotosPDF,
)


def crear_fotografia(ruta):
    """Crea una fotografía PNG para las pruebas."""

    imagen = QImage(
        120,
        80,
        QImage.Format.Format_RGB32,
    )

    imagen.fill(Qt.GlobalColor.white)

    assert imagen.save(str(ruta), "PNG")

    return ruta


def test_servicio_delega_al_motor(monkeypatch):
    """Comprueba que se llama al motor con los argumentos."""

    gestor = GestorFotografias()
    destino = "resultado.pdf"

    resultado_esperado = ResultadoFotosPDF(
        ruta_destino=destino,
        numero_paginas=2,
        tamano_bytes=5000,
    )

    llamadas = []

    def motor_simulado(gestor_recibido, destino_recibido):
        llamadas.append(
            (gestor_recibido, destino_recibido)
        )
        return resultado_esperado

    monkeypatch.setattr(
        modulo_servicio,
        "generar_pdf_fotografias",
        motor_simulado,
    )

    servicio = ServicioFotosPDF()

    resultado = servicio.generar(gestor, destino)

    assert llamadas == [(gestor, destino)]
    assert resultado is resultado_esperado


def test_servicio_propaga_error_motor(monkeypatch):
    """No debe ocultar errores del generador PDF."""

    def motor_simulado(gestor, destino):
        raise ErrorFotosPDF(
            "No fue posible generar el documento."
        )

    monkeypatch.setattr(
        modulo_servicio,
        "generar_pdf_fotografias",
        motor_simulado,
    )

    servicio = ServicioFotosPDF()

    with pytest.raises(
        ErrorFotosPDF,
        match="No fue posible generar",
    ):
        servicio.generar(
            GestorFotografias(),
            "resultado.pdf",
        )


def test_servicio_propaga_destino_existente(monkeypatch):
    """Debe conservar la protección contra sobrescritura."""

    def motor_simulado(gestor, destino):
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    monkeypatch.setattr(
        modulo_servicio,
        "generar_pdf_fotografias",
        motor_simulado,
    )

    servicio = ServicioFotosPDF()

    with pytest.raises(FileExistsError):
        servicio.generar(
            GestorFotografias(),
            "existente.pdf",
        )


def test_servicio_propaga_gestor_vacio():
    """El motor debe rechazar colecciones vacías."""

    servicio = ServicioFotosPDF()
    gestor = GestorFotografias()

    with pytest.raises(ValueError):
        servicio.generar(
            gestor,
            "resultado.pdf",
        )


def test_servicio_integracion_real(tmp_path):
    """
    Comprueba el recorrido completo:
    gestor -> servicio -> motor -> PDF.
    """

    ruta_fotografia = crear_fotografia(
        tmp_path / "clase.png"
    )

    gestor = GestorFotografias()
    gestor.agregar_fotografia(ruta_fotografia)

    ruta_destino = tmp_path / "clase.pdf"

    servicio = ServicioFotosPDF()

    resultado = servicio.generar(
        gestor,
        ruta_destino,
    )

    assert resultado.ruta_destino == ruta_destino
    assert resultado.numero_paginas == 1
    assert resultado.tamano_bytes > 0

    assert ruta_destino.exists()
    assert ruta_fotografia.exists()

    with pymupdf.open(ruta_destino) as documento:
        assert documento.page_count == 1
        assert documento[0].get_images(full=True)
