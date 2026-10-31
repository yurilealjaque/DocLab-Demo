
"""
Pruebas del plan de reconstruccion Word.
"""

import pytest

from doclab.document_engine.pdf_layout import (
    BloquePDF,
    ResultadoEstructuraPDF
)

from doclab.document_engine.ocr_document import (
    ResultadoPaginaOCR,
    ResultadoDocumentoOCR
)

from doclab.document_engine.word_layout_plan import (
    crear_plan_word
)


def crear_pagina_ocr(metodo, texto, numero=1):
    return ResultadoPaginaOCR(
        numero_pagina=numero,
        texto=texto,
        metodo=metodo
    )


def crear_bloque(tipo, y, texto=""):
    return BloquePDF(
        numero_pagina=1,
        tipo=tipo,
        coordenadas=(50, y, 250, y + 30),
        texto=texto
    )


def test_orden_digital_con_imagen():
    titulo = crear_bloque("texto", 40, "Titulo")
    imagen = crear_bloque("imagen", 120)
    parrafo = crear_bloque("texto", 300, "Parrafo")

    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_pagina_ocr("digital", "Titulo\nParrafo"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(parrafo, imagen, titulo)
    )

    plan = crear_plan_word(ocr, estructura)

    assert tuple(
        elemento.tipo for elemento in plan.elementos
    ) == ("texto", "imagen", "texto")

    assert plan.elementos[0].texto == "Titulo"
    assert plan.elementos[2].texto == "Parrafo"


def test_ocr_parcial_no_duplica_texto():
    texto = crear_bloque(
        "texto", 40, "ENCABEZADO DIGITAL"
    )
    imagen = crear_bloque("imagen", 120)

    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(
            crear_pagina_ocr(
                "ocr_parcial",
                "ENCABEZADO DIGITAL\nCODIGO IMAGEN"
            ),
        )
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(texto, imagen)
    )

    plan = crear_plan_word(ocr, estructura)

    textos = [
        elemento.texto
        for elemento in plan.elementos
        if elemento.tipo == "texto"
    ]

    assert len(textos) == 1
    assert textos[0].count("ENCABEZADO DIGITAL") == 1
    assert "CODIGO IMAGEN" in textos[0]
    assert sum(
        elemento.tipo == "imagen"
        for elemento in plan.elementos
    ) == 1


def test_ocr_completo_no_repite_imagen():
    imagen = crear_bloque("imagen", 0)

    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(
            crear_pagina_ocr(
                "ocr_completo",
                "FACTURA RECONOCIDA"
            ),
        )
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(imagen,)
    )

    plan = crear_plan_word(ocr, estructura)

    assert len(plan.elementos) == 1
    assert plan.elementos[0].tipo == "texto"
    assert plan.elementos[0].texto == "FACTURA RECONOCIDA"


def test_pagina_vacia():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_pagina_ocr("vacia", ""),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=()
    )

    plan = crear_plan_word(ocr, estructura)

    assert plan.total_paginas == 1
    assert plan.elementos == ()


def test_rechazar_cantidad_paginas_distinta():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_pagina_ocr("digital", "Texto"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=2,
        bloques=()
    )

    with pytest.raises(ValueError):
        crear_plan_word(ocr, estructura)


def test_no_modificar_estructura_original():
    inferior = crear_bloque("texto", 300, "Inferior")
    superior = crear_bloque("texto", 40, "Superior")

    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_pagina_ocr("digital", "Texto"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(inferior, superior)
    )

    crear_plan_word(ocr, estructura)

    assert estructura.bloques == (inferior, superior)
