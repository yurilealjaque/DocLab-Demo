
import pytest

from docx import Document

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR,
    ResultadoPaginaOCR
)

from doclab.document_engine.ocr_word_export import (
    exportar_ocr_a_word
)


def crear_resultado_simulado():
    return ResultadoDocumentoOCR(
        total_paginas=2,
        paginas=(
            ResultadoPaginaOCR(
                numero_pagina=1,
                texto="Hola desde DocLab",
                metodo="digital"
            ),
            ResultadoPaginaOCR(
                numero_pagina=2,
                texto="Texto reconocido mediante OCR",
                metodo="ocr_completo"
            )
        )
    )


def test_exportacion_word(tmp_path):
    destino = tmp_path / "resultado.docx"

    resultado = crear_resultado_simulado()

    ruta = exportar_ocr_a_word(
        resultado,
        destino
    )

    assert ruta == str(destino)
    assert destino.is_file()

    documento = Document(str(destino))

    contenido = "\n".join(
        parrafo.text for parrafo in documento.paragraphs
    )

    assert "Hola desde DocLab" in contenido
    assert "Texto reconocido mediante OCR" in contenido


def test_evitar_sobrescritura(tmp_path):
    destino = tmp_path / "existente.docx"

    destino.write_bytes(b"Archivo original")

    with pytest.raises(FileExistsError):
        exportar_ocr_a_word(
            crear_resultado_simulado(),
            destino
        )

    assert destino.read_bytes() == b"Archivo original"


def test_extension_incorrecta(tmp_path):
    destino = tmp_path / "resultado.txt"

    with pytest.raises(ValueError):
        exportar_ocr_a_word(
            crear_resultado_simulado(),
            destino
        )


def test_resultado_inconsistente(tmp_path):
    destino = tmp_path / "resultado.docx"

    resultado = ResultadoDocumentoOCR(
        total_paginas=3,
        paginas=(
            ResultadoPaginaOCR(
                numero_pagina=1,
                texto="Texto de prueba",
                metodo="digital"
            ),
        )
    )

    with pytest.raises(ValueError):
        exportar_ocr_a_word(
            resultado,
            destino
        )

    assert not destino.exists()
