
"""
Pruebas de los mensajes de resultado de DocLab.

Verifica:
- Conversión PDF a Word exitosa.
- Error durante la conversión.
- División PDF exitosa.
- Error durante la división.
"""

import pytest

from PySide6.QtWidgets import QApplication

from doclab.ui.pages.converter_page import PaginaConversor
from doclab.ui.pages.pdf_split_page import PaginaDivisionPDF


@pytest.fixture(scope="module")
def aplicacion_qt():
    """Crea una aplicación Qt para las pruebas."""

    aplicacion = QApplication.instance()

    if aplicacion is None:
        aplicacion = QApplication([])

    yield aplicacion


@pytest.fixture
def pagina_conversion(aplicacion_qt):
    """Prepara la pantalla de conversión."""

    pagina = PaginaConversor()

    yield pagina

    pagina.close()


@pytest.fixture
def pagina_division(aplicacion_qt):
    """Prepara la pantalla de división."""

    pagina = PaginaDivisionPDF()

    yield pagina

    pagina.close()


def test_mensaje_conversion_exitosa(
    pagina_conversion,
    monkeypatch
):
    """Verifica el mensaje de conversión exitosa."""

    mensajes = []

    def simular_mensaje(ventana, titulo, contenido):
        mensajes.append((titulo, contenido))

    monkeypatch.setattr(
        "doclab.ui.pages.converter_page.QMessageBox.information",
        simular_mensaje
    )

    ruta = "C:/Documentos/resultado.docx"

    pagina_conversion.conversion_completada(ruta)

    assert len(mensajes) == 1
    assert mensajes[0][0] == "Documento Word generado"
    assert ruta in mensajes[0][1]
    assert "revisar el contenido y formato" in mensajes[0][1]
    assert pagina_conversion.etiqueta_estado.text() == (
        "Conversión finalizada correctamente."
    )


def test_mensaje_error_conversion(
    pagina_conversion,
    monkeypatch
):
    """Verifica que se conserve el detalle del error."""

    mensajes = []

    def simular_error(ventana, titulo, contenido):
        mensajes.append((titulo, contenido))

    monkeypatch.setattr(
        "doclab.ui.pages.converter_page.QMessageBox.critical",
        simular_error
    )

    error_original = "El PDF está protegido."

    pagina_conversion.conversion_con_error(error_original)

    assert len(mensajes) == 1
    assert mensajes[0][0] == (
        "No se pudo completar la conversión"
    )
    assert error_original in mensajes[0][1]
    assert "Detalle del problema:" in mensajes[0][1]
    assert pagina_conversion.etiqueta_estado.text() == (
        "No se pudo convertir el documento."
    )


def test_mensaje_division_exitosa(
    pagina_division,
    monkeypatch
):
    """Verifica la cantidad de documentos generados."""

    mensajes = []

    def simular_mensaje(ventana, titulo, contenido):
        mensajes.append((titulo, contenido))

    monkeypatch.setattr(
        "doclab.ui.pages.pdf_split_page.QMessageBox.information",
        simular_mensaje
    )

    rutas = [
        "C:/Documentos/pagina_1.pdf",
        "C:/Documentos/pagina_2.pdf",
        "C:/Documentos/pagina_3.pdf",
    ]

    pagina_division.mostrar_resultado(rutas)

    assert len(mensajes) == 1
    assert mensajes[0][0] == "División completada"
    assert "3 documentos PDF" in mensajes[0][1]
    assert pagina_division.etiqueta_estado.text() == (
        "División completada: 3 archivo(s) generado(s)."
    )


def test_mensaje_error_division(
    pagina_division,
    monkeypatch
):
    """Verifica el mensaje de error en la división."""

    mensajes = []

    def simular_error(ventana, titulo, contenido):
        mensajes.append((titulo, contenido))

    monkeypatch.setattr(
        "doclab.ui.pages.pdf_split_page.QMessageBox.critical",
        simular_error
    )

    error_original = "No se puede leer el documento PDF."

    pagina_division.mostrar_error(error_original)

    assert len(mensajes) == 1
    assert mensajes[0][0] == (
        "No se pudo completar la división"
    )
    assert error_original in mensajes[0][1]
    assert "Detalle del problema:" in mensajes[0][1]
    assert pagina_division.etiqueta_estado.text() == (
        "No se pudo completar la división."
    )
