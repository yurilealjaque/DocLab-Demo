
"""
Pruebas automatizadas de la pantalla Unir PDF.

Comprueban:
- Incorporacion de archivos.
- Prevencion de duplicados.
- Ordenamiento.
- Eliminacion.
- Sincronizacion entre interfaz y rutas internas.
"""

import pytest

from PySide6.QtWidgets import QApplication

from doclab.ui.pages.pdf_merge_page import PaginaUnionPDF


@pytest.fixture(scope="module")
def aplicacion_qt():
    """
    Crea una aplicacion Qt si no existe.
    Conserva la referencia durante las pruebas.
    """
    aplicacion = QApplication.instance()

    if aplicacion is None:
        aplicacion = QApplication([])

    yield aplicacion


@pytest.fixture
def pagina_union(aplicacion_qt):
    """
    Entrega una pantalla nueva para cada prueba.
    """
    pagina = PaginaUnionPDF()

    yield pagina

    pagina.close()


@pytest.fixture
def archivos_pdf(tmp_path):
    """
    Crea tres archivos de prueba en una
    carpeta temporal.
    """
    rutas = []

    for nombre in ["a.pdf", "b.pdf", "c.pdf"]:
        ruta = tmp_path / nombre
        ruta.write_bytes(b"PDF simulado")
        rutas.append(ruta)

    return rutas


def test_agregar_archivos(pagina_union, archivos_pdf):
    pagina_union.agregar_archivos(archivos_pdf)

    assert len(pagina_union.rutas_pdf) == 3
    assert pagina_union.lista_archivos.count() == 3
    assert pagina_union.etiqueta_contador.text() == (
        "3 archivos seleccionados"
    )


def test_evitar_archivos_duplicados(
    pagina_union,
    archivos_pdf
):
    pagina_union.agregar_archivos([
        archivos_pdf[0],
        archivos_pdf[0],
        archivos_pdf[1]
    ])

    assert len(pagina_union.rutas_pdf) == 2
    assert pagina_union.lista_archivos.count() == 2


def test_subir_archivo(pagina_union, archivos_pdf):
    pagina_union.agregar_archivos(archivos_pdf)

    # Seleccionar el segundo documento.
    pagina_union.lista_archivos.setCurrentRow(1)

    pagina_union.subir_archivo()

    assert pagina_union.rutas_pdf[0] == str(
        archivos_pdf[1].resolve()
    )

    assert pagina_union.lista_archivos.item(0).text() == (
        "b.pdf"
    )

    assert pagina_union.lista_archivos.currentRow() == 0


def test_bajar_archivo(pagina_union, archivos_pdf):
    pagina_union.agregar_archivos(archivos_pdf)

    # Seleccionar el primer documento.
    pagina_union.lista_archivos.setCurrentRow(0)

    pagina_union.bajar_archivo()

    assert pagina_union.rutas_pdf[1] == str(
        archivos_pdf[0].resolve()
    )

    assert pagina_union.lista_archivos.item(1).text() == (
        "a.pdf"
    )

    assert pagina_union.lista_archivos.currentRow() == 1


def test_eliminar_archivo(pagina_union, archivos_pdf):
    pagina_union.agregar_archivos(archivos_pdf)

    pagina_union.lista_archivos.setCurrentRow(1)
    pagina_union.eliminar_archivo()

    assert len(pagina_union.rutas_pdf) == 2
    assert pagina_union.lista_archivos.count() == 2

    assert pagina_union.etiqueta_contador.text() == (
        "2 archivos seleccionados"
    )

    # Eliminar de la lista no borra el archivo real.
    assert archivos_pdf[1].exists()


def test_sincronizacion_orden(pagina_union, archivos_pdf):
    pagina_union.agregar_archivos(archivos_pdf)

    # Mover el tercer documento hasta el inicio.
    pagina_union.lista_archivos.setCurrentRow(2)

    pagina_union.subir_archivo()
    pagina_union.subir_archivo()

    orden_interno = [
        ruta.split("/")[-1].split("\\")[-1]
        for ruta in pagina_union.rutas_pdf
    ]

    orden_visual = [
        pagina_union.lista_archivos.item(i).text()
        for i in range(pagina_union.lista_archivos.count())
    ]

    assert orden_interno == orden_visual
    assert orden_visual == [
        "c.pdf",
        "a.pdf",
        "b.pdf"
    ]
