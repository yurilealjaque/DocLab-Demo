
"""
Pruebas del exportador Word basado en bloques.
"""

import pytest
import pymupdf

from docx import Document

from doclab.document_engine.word_layout_plan import (
    ElementoPlanWord,
    ResultadoPlanWord
)

from doclab.document_engine.pdf_image_extractor import (
    ImagenExtraidaPDF,
    ResultadoImagenesPDF
)

from doclab.document_engine.word_layout_export import (
    exportar_plan_a_word
)


def crear_imagen_png():
    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)

    return imagen.tobytes("png")


def crear_elemento(tipo, texto="", numero=1, y=50):
    return ElementoPlanWord(
        numero_pagina=numero,
        tipo=tipo,
        texto=texto,
        coordenadas=(50, y, 150, y + 100)
    )


def crear_imagen(numero=1, y=50):
    return ImagenExtraidaPDF(
        numero_pagina=numero,
        coordenadas=(50, y, 150, y + 100),
        formato="png",
        datos=crear_imagen_png()
    )


def test_word_respeta_orden_de_bloques(tmp_path):
    destino = tmp_path / "ordenado.docx"

    plan = ResultadoPlanWord(
        total_paginas=1,
        elementos=(
            crear_elemento("texto", "TITULO", y=20),
            crear_elemento("imagen", y=100),
            crear_elemento("texto", "PARRAFO", y=250),
        )
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=(crear_imagen(y=100),)
    )

    exportar_plan_a_word(plan, imagenes, destino)

    documento = Document(str(destino))

    # Revisar el contenido en el orden
    # de los parrafos del documento.
    secuencia = []

    for parrafo in documento.paragraphs:

        if parrafo._p.xpath(".//w:drawing"):
            secuencia.append("IMAGEN")

        elif parrafo.text.strip():
            secuencia.append(parrafo.text)

    assert secuencia == [
        "TITULO",
        "IMAGEN",
        "PARRAFO"
    ]

    assert len(documento.inline_shapes) == 1


def test_imagenes_repetidas_se_insertan_dos_veces(tmp_path):
    destino = tmp_path / "repetidas.docx"

    plan = ResultadoPlanWord(
        total_paginas=1,
        elementos=(
            crear_elemento("imagen", y=50),
            crear_elemento("imagen", y=200),
        )
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=(
            crear_imagen(y=50),
            crear_imagen(y=200),
        )
    )

    exportar_plan_a_word(plan, imagenes, destino)

    documento = Document(str(destino))

    assert len(documento.inline_shapes) == 2


def test_plan_ocr_solo_texto(tmp_path):
    destino = tmp_path / "ocr.docx"

    plan = ResultadoPlanWord(
        total_paginas=1,
        elementos=(
            crear_elemento(
                "texto",
                "FACTURA RECONOCIDA",
            ),
        )
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=()
    )

    exportar_plan_a_word(plan, imagenes, destino)

    documento = Document(str(destino))

    contenido = " ".join(
        parrafo.text for parrafo in documento.paragraphs
    )

    assert "FACTURA RECONOCIDA" in contenido
    assert len(documento.inline_shapes) == 0


def test_imagen_sin_correspondencia(tmp_path):
    destino = tmp_path / "sin_imagen.docx"

    plan = ResultadoPlanWord(
        total_paginas=1,
        elementos=(
            crear_elemento("imagen", y=100),
        )
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=()
    )

    with pytest.raises(ValueError):
        exportar_plan_a_word(
            plan,
            imagenes,
            destino
        )

    assert not destino.exists()


def test_rechazar_distinta_cantidad_de_paginas(tmp_path):
    destino = tmp_path / "inconsistente.docx"

    plan = ResultadoPlanWord(
        total_paginas=2,
        elementos=()
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=()
    )

    with pytest.raises(ValueError):
        exportar_plan_a_word(
            plan,
            imagenes,
            destino
        )


def test_no_sobrescribir_documento_existente(tmp_path):
    destino = tmp_path / "existente.docx"
    destino.write_bytes(b"Contenido original")

    plan = ResultadoPlanWord(
        total_paginas=1,
        elementos=()
    )

    imagenes = ResultadoImagenesPDF(
        total_paginas=1,
        imagenes=()
    )

    with pytest.raises(FileExistsError):
        exportar_plan_a_word(
            plan,
            imagenes,
            destino
        )

    assert destino.read_bytes() == b"Contenido original"
