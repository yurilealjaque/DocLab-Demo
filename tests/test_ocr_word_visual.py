
import pytest
import pymupdf

from docx import Document

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR,
    ResultadoPaginaOCR
)

from doclab.document_engine.pdf_image_extractor import (
    ImagenExtraidaPDF,
    ResultadoImagenesPDF
)

from doclab.document_engine.ocr_word_visual import (
    exportar_word_con_imagenes
)


def crear_imagen_png():
    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)
    return imagen.tobytes("png")


def crear_resultado_ocr():
    return ResultadoDocumentoOCR(
        total_paginas=2,
        paginas=(
            ResultadoPaginaOCR(
                numero_pagina=1,
                texto="Titulo digital\nTexto reconocido",
                metodo="ocr_parcial"
            ),
            ResultadoPaginaOCR(
                numero_pagina=2,
                texto="FACTURA ESCANEADA",
                metodo="ocr_completo"
            )
        )
    )


def crear_resultado_imagenes():
    datos = crear_imagen_png()

    return ResultadoImagenesPDF(
        total_paginas=2,
        imagenes=(
            ImagenExtraidaPDF(
                numero_pagina=1,
                coordenadas=(50, 100, 200, 250),
                formato="png",
                datos=datos
            ),
            ImagenExtraidaPDF(
                numero_pagina=2,
                coordenadas=(0, 0, 500, 700),
                formato="png",
                datos=datos
            )
        )
    )


def test_word_contiene_texto_e_imagen(tmp_path):
    destino = tmp_path / "visual.docx"

    exportar_word_con_imagenes(
        crear_resultado_ocr(),
        crear_resultado_imagenes(),
        destino
    )

    documento = Document(str(destino))

    texto = " ".join(
        parrafo.text
        for parrafo in documento.paragraphs
    )

    assert "Titulo digital" in texto
    assert "Texto reconocido" in texto
    assert "FACTURA ESCANEADA" in texto

    # Solo la imagen de la pagina mixta.
    assert len(documento.inline_shapes) == 1


def test_word_no_repite_imagen_escaneada(tmp_path):
    destino = tmp_path / "escaneo.docx"

    exportar_word_con_imagenes(
        crear_resultado_ocr(),
        crear_resultado_imagenes(),
        destino
    )

    documento = Document(str(destino))

    assert len(documento.inline_shapes) == 1


def test_word_no_sobrescribe_archivo(tmp_path):
    destino = tmp_path / "existente.docx"

    destino.write_bytes(b"Contenido original")

    with pytest.raises(FileExistsError):
        exportar_word_con_imagenes(
            crear_resultado_ocr(),
            crear_resultado_imagenes(),
            destino
        )

    assert destino.read_bytes() == b"Contenido original"


def test_resultados_de_distintos_documentos(tmp_path):
    destino = tmp_path / "incorrecto.docx"

    imagenes = ResultadoImagenesPDF(
        total_paginas=3,
        imagenes=()
    )

    with pytest.raises(ValueError):
        exportar_word_con_imagenes(
            crear_resultado_ocr(),
            imagenes,
            destino
        )

    assert not destino.exists()


def test_rechazar_formato_no_compatible(tmp_path):
    destino = tmp_path / "formato.docx"

    imagenes = ResultadoImagenesPDF(
        total_paginas=2,
        imagenes=(
            ImagenExtraidaPDF(
                numero_pagina=1,
                coordenadas=(10, 10, 100, 100),
                formato="jpx",
                datos=b"datos_simulados"
            ),
        )
    )

    with pytest.raises(ValueError):
        exportar_word_con_imagenes(
            crear_resultado_ocr(),
            imagenes,
            destino
        )

    assert not destino.exists()
