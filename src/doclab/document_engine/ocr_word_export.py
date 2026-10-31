
"""
Exportacion de resultados OCR a documentos Word.

Genera un DOCX editable a partir de los textos
extraidos por el procesador OCR de DocLab.

Esta primera version conserva el texto y
la separacion entre paginas, pero no reconstruye
el formato visual original del PDF.
"""

import os
import tempfile
from pathlib import Path

from docx import Document

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR
)

from doclab.document_engine.pdf_to_word import (
    validar_documento_word
)


def exportar_ocr_a_word(
    resultado: ResultadoDocumentoOCR,
    ruta_destino
):
    """
    Exporta los textos de un ResultadoDocumentoOCR.

    Evita sobrescribir archivos existentes.
    Utiliza un archivo temporal antes de publicar
    el documento final.

    Retorna:
        str: Ruta del Word generado.
    """

    destino = Path(ruta_destino)

    # 1. Validar el destino.
    if destino.suffix.lower() != ".docx":
        raise ValueError(
            "El archivo de destino debe ser DOCX."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    if destino.exists():
        raise FileExistsError(
            "El documento de destino ya existe."
        )

    # 2. Verificar la consistencia del resultado.
    if resultado.total_paginas != len(resultado.paginas):
        raise ValueError(
            "El numero de paginas del resultado "
            "OCR no coincide con su contenido."
        )

    # 3. Crear el documento Word en memoria.
    documento_word = Document()

    for indice, pagina in enumerate(resultado.paginas):

        # Separar cada pagina del documento.
        if indice > 0:
            documento_word.add_page_break()

        # Agregar el texto recuperado.
        lineas = pagina.texto.splitlines()

        for linea in lineas:
            documento_word.add_paragraph(linea)

    # 4. Crear un archivo temporal en el destino.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_ocr_",
        suffix=".docx",
        dir=destino.parent
    )

    os.close(descriptor)

    temporal = Path(ruta_temporal)

    try:
        # 5. Guardar primero en el temporal.
        documento_word.save(str(temporal))

        # 6. Validar el archivo generado.
        validar_documento_word(temporal)

        # 7. Publicar sin sobrescribir.
        os.link(temporal, destino)

        return str(destino)

    finally:
        # 8. Limpiar siempre nuestro temporal.
        temporal.unlink(missing_ok=True)
