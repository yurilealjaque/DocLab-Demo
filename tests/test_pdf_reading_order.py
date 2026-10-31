
"""
Pruebas del ordenamiento geometrico
de bloques de PDF en DocLab.
"""

import pytest
import pymupdf

from doclab.document_engine.pdf_layout import (
    BloquePDF,
    ResultadoEstructuraPDF,
    analizar_estructura_pdf
)

from doclab.document_engine.pdf_reading_order import (
    ordenar_bloques_por_posicion
)


def crear_bloque(numero, tipo, x, y):
    return BloquePDF(
        numero_pagina=numero,
        tipo=tipo,
        coordenadas=(x, y, x + 100, y + 30),
        texto=tipo if tipo == "texto" else ""
    )


def test_orden_vertical():
    parrafo = crear_bloque(1, "texto", 50, 300)
    titulo = crear_bloque(1, "texto", 50, 40)
    imagen = crear_bloque(1, "imagen", 50, 120)

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(parrafo, imagen, titulo)
    )

    resultado = ordenar_bloques_por_posicion(
        estructura
    )

    assert resultado.bloques == (
        titulo,
        imagen,
        parrafo
    )


def test_orden_por_paginas():
    segunda = crear_bloque(2, "texto", 50, 20)
    primera = crear_bloque(1, "texto", 50, 300)

    estructura = ResultadoEstructuraPDF(
        total_paginas=2,
        bloques=(segunda, primera)
    )

    resultado = ordenar_bloques_por_posicion(
        estructura
    )

    assert resultado.bloques == (
        primera,
        segunda
    )


def test_orden_horizontal_misma_altura():
    derecha = crear_bloque(1, "texto", 250, 100)
    izquierda = crear_bloque(1, "texto", 50, 100)

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(derecha, izquierda)
    )

    resultado = ordenar_bloques_por_posicion(
        estructura
    )

    assert resultado.bloques == (
        izquierda,
        derecha
    )


def test_no_modificar_resultado_original():
    inferior = crear_bloque(1, "texto", 50, 300)
    superior = crear_bloque(1, "texto", 50, 50)

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(inferior, superior)
    )

    ordenar_bloques_por_posicion(estructura)

    assert estructura.bloques == (
        inferior,
        superior
    )


def test_integracion_pdf_real(tmp_path):
    ruta_pdf = tmp_path / "orden.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page(
            width=400,
            height=500
        )

        # Insertar primero el texto inferior.
        pagina.insert_text(
            (50, 300),
            "PARRAFO INFERIOR",
            fontsize=14
        )

        # Insertar despues el titulo superior.
        pagina.insert_text(
            (50, 60),
            "TITULO SUPERIOR",
            fontsize=14
        )

        documento.save(str(ruta_pdf))

    estructura = analizar_estructura_pdf(ruta_pdf)

    resultado = ordenar_bloques_por_posicion(
        estructura
    )

    textos = [
        bloque.texto
        for bloque in resultado.bloques
        if bloque.tipo == "texto"
    ]

    assert len(textos) == 2
    assert "TITULO SUPERIOR" in textos[0]
    assert "PARRAFO INFERIOR" in textos[1]
