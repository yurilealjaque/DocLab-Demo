
"""
Pruebas del plan Word con coordenadas OCR.
"""

import pytest

from doclab.document_engine.ocr_document import (
    ResultadoPaginaOCR,
    ResultadoDocumentoOCR
)

from doclab.document_engine.ocr_text_blocks import (
    FragmentoTextoPDF,
    ResultadoTextoPosicionado
)

from doclab.document_engine.pdf_layout import (
    BloquePDF,
    ResultadoEstructuraPDF
)

from doclab.document_engine.word_positioned_plan import (
    crear_plan_word_posicionado
)


def crear_fragmento(
    texto,
    y,
    origen="ocr",
    numero=1
):
    return FragmentoTextoPDF(
        numero_pagina=numero,
        texto=texto,
        coordenadas=(50, y, 250, y + 20),
        origen=origen
    )


def crear_bloque(tipo, y, texto="", numero=1):
    return BloquePDF(
        numero_pagina=numero,
        tipo=tipo,
        coordenadas=(50, y, 250, y + 40),
        texto=texto
    )


def crear_ocr(metodo, texto="", numero=1):
    return ResultadoPaginaOCR(
        numero_pagina=numero,
        texto=texto,
        metodo=metodo
    )


def test_ocr_parcial_con_coordenadas():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(
            crear_ocr(
                "ocr_parcial",
                "TITULO DIGITAL\nFACTURA 2026"
            ),
        )
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(
            crear_bloque("imagen", 100),
            crear_bloque("texto", 30, "TITULO DIGITAL")
        )
    )

    posicionados = (
        ResultadoTextoPosicionado(
            numero_pagina=1,
            fragmentos=(
                crear_fragmento(
                    "FACTURA 2026",
                    150,
                    origen="ocr"
                ),
                crear_fragmento(
                    "TITULO DIGITAL",
                    30,
                    origen="digital"
                )
            )
        ),
    )

    plan = crear_plan_word_posicionado(
        ocr,
        estructura,
        posicionados
    )

    assert tuple(
        elemento.texto if elemento.tipo == "texto"
        else "IMAGEN"
        for elemento in plan.elementos
    ) == (
        "TITULO DIGITAL",
        "IMAGEN",
        "FACTURA 2026"
    )

    assert plan.elementos[2].coordenadas == (
        50, 150, 250, 170
    )


def test_ocr_parcial_no_duplica_texto_digital():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_ocr("ocr_parcial"),)
    )

    estructura = ResultadoEstructuraPDF(
    total_paginas=1,
    bloques=(
        crear_bloque("texto", 30, "ENCABEZADO"),)
    )

    posicionados = (
        ResultadoTextoPosicionado(
            numero_pagina=1,
            fragmentos=(
                crear_fragmento(
                    "ENCABEZADO",
                    30,
                    origen="digital"
                ),
                crear_fragmento(
                    "CODIGO 5678",
                    120,
                    origen="ocr"
                )
            )
        ),
    )

    plan = crear_plan_word_posicionado(
        ocr,
        estructura,
        posicionados
    )

    textos = [
        elemento.texto
        for elemento in plan.elementos
        if elemento.tipo == "texto"
    ]

    assert textos.count("ENCABEZADO") == 1
    assert "CODIGO 5678" in textos


def test_ocr_completo_omite_imagen():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_ocr("ocr_completo"),
        )
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(
            crear_bloque("imagen", 0),
        )
    )

    posicionados = (
        ResultadoTextoPosicionado(
            numero_pagina=1,
            fragmentos=(
                crear_fragmento(
                    "FACTURA ESCANEADA",
                    100
                ),
            )
        ),
    )

    plan = crear_plan_word_posicionado(
        ocr,
        estructura,
        posicionados
    )

    assert len(plan.elementos) == 1
    assert plan.elementos[0].tipo == "texto"
    assert plan.elementos[0].texto == "FACTURA ESCANEADA"


def test_pagina_digital_sin_ocr_posicionado():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_ocr("digital"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=(
            crear_bloque("texto", 200, "PARRAFO"),
            crear_bloque("texto", 40, "TITULO")
        )
    )

    plan = crear_plan_word_posicionado(
        ocr,
        estructura,
        ()
    )

    assert tuple(
        elemento.texto
        for elemento in plan.elementos
    ) == ("TITULO", "PARRAFO")


def test_faltan_fragmentos_ocr():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_ocr("ocr_parcial"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=()
    )

    with pytest.raises(ValueError):
        crear_plan_word_posicionado(
            ocr,
            estructura,
            ()
        )


def test_rechazar_resultado_posicionado_duplicado():
    ocr = ResultadoDocumentoOCR(
        total_paginas=1,
        paginas=(crear_ocr("ocr_completo"),)
    )

    estructura = ResultadoEstructuraPDF(
        total_paginas=1,
        bloques=()
    )

    pagina = ResultadoTextoPosicionado(
        numero_pagina=1,
        fragmentos=()
    )

    with pytest.raises(ValueError):
        crear_plan_word_posicionado(
            ocr,
            estructura,
            (pagina, pagina)
        )
