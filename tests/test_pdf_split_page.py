
"""
Pruebas de la interfaz de division PDF.
"""

import pytest
import pymupdf

from PySide6.QtWidgets import QApplication

from doclab.ui.pages.pdf_split_page import (
    PaginaDivisionPDF,
)


@pytest.fixture(scope="module")
def aplicacion():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@pytest.fixture
def pagina(aplicacion):
    ventana = PaginaDivisionPDF()

    yield ventana

    ventana.close()


def crear_pdf(ruta, cantidad_paginas):
    with pymupdf.open() as documento:
        for numero in range(cantidad_paginas):
            documento.new_page()

        documento.save(str(ruta))


def test_cargar_pdf_actualiza_controles(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 8)

    pagina.cargar_pdf(origen)

    assert pagina.ruta_pdf == str(origen)
    assert pagina.total_paginas == 8

    assert pagina.pagina_inicio.maximum() == 8
    assert pagina.pagina_fin.maximum() == 8

    assert pagina.pagina_inicio.value() == 1
    assert pagina.pagina_fin.value() == 8


def test_modalidades_de_division(pagina):
    pagina.selector_modo.setCurrentIndex(0)

    assert pagina.obtener_modo() == "rango"
    assert not pagina.grupo_paginas.isVisible()

    pagina.selector_modo.setCurrentIndex(1)

    assert pagina.obtener_modo() == "paginas"

    pagina.selector_modo.setCurrentIndex(2)

    assert pagina.obtener_modo() == "todas"


def test_interpreta_paginas_especificas(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 10)

    pagina.cargar_pdf(origen)

    pagina.entrada_paginas.setText(
        "1, 4, 8"
    )

    resultado = (
        pagina.obtener_paginas_especificas()
    )

    assert resultado == [1, 4, 8]


def test_rechaza_paginas_fuera_de_rango(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 5)

    pagina.cargar_pdf(origen)

    pagina.entrada_paginas.setText(
        "1, 3, 9"
    )

    with pytest.raises(ValueError):
        pagina.obtener_paginas_especificas()


def test_rechaza_paginas_repetidas(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 5)

    pagina.cargar_pdf(origen)

    pagina.entrada_paginas.setText(
        "1, 3, 3"
    )

    with pytest.raises(ValueError):
        pagina.obtener_paginas_especificas()


def test_boton_se_activa_con_datos_completos(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 5)

    assert not pagina.boton_dividir.isEnabled()

    pagina.cargar_pdf(origen)

    assert not pagina.boton_dividir.isEnabled()

    pagina.ruta_destino = str(
        tmp_path / "resultado.pdf"
    )

    pagina.actualizar_boton_dividir()

    assert pagina.boton_dividir.isEnabled()


def test_preparar_solicitud_por_rango(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 8)

    pagina.cargar_pdf(origen)
    pagina.ruta_destino = str(
        tmp_path / "resultado.pdf"
    )

    pagina.pagina_inicio.setValue(2)
    pagina.pagina_fin.setValue(6)

    solicitud = pagina.preparar_solicitud()

    assert solicitud == {
        "modo": "rango",
        "ruta_origen": str(origen),
        "ruta_destino": str(
            tmp_path / "resultado.pdf"
        ),
        "pagina_inicio": 2,
        "pagina_fin": 6,
    }


def test_preparar_solicitud_paginas_especificas(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 10)

    pagina.cargar_pdf(origen)
    pagina.selector_modo.setCurrentIndex(1)

    pagina.ruta_destino = str(
        tmp_path / "seleccion.pdf"
    )

    pagina.entrada_paginas.setText("1, 4, 8")

    solicitud = pagina.preparar_solicitud()

    assert solicitud["modo"] == "paginas"
    assert solicitud["paginas"] == [1, 4, 8]


def test_preparar_solicitud_separar_todas(
    pagina,
    tmp_path
):
    origen = tmp_path / "documento.pdf"
    crear_pdf(origen, 4)

    pagina.cargar_pdf(origen)
    pagina.selector_modo.setCurrentIndex(2)

    carpeta = tmp_path / "salida"
    carpeta.mkdir()

    pagina.ruta_destino = str(carpeta)

    solicitud = pagina.preparar_solicitud()

    assert solicitud == {
        "modo": "todas",
        "ruta_origen": str(origen),
        "ruta_destino": str(carpeta),
    }
