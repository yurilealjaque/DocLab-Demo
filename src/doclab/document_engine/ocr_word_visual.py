
"""
Exportacion de documentos OCR a Word con imagenes.

Combina resultados de:
- Procesamiento OCR por pagina.
- Extraccion de imagenes del PDF.

Primera version: las imagenes se insertan
en linea, sin reconstruir su posicion exacta.
"""

import os
import tempfile

from io import BytesIO
from pathlib import Path

from docx import Document
from docx.shared import Inches

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR
)

from doclab.document_engine.pdf_image_extractor import (
    ResultadoImagenesPDF
)

from doclab.document_engine.pdf_to_word import (
    validar_documento_word
)


def exportar_word_con_imagenes(
    resultado_ocr: ResultadoDocumentoOCR,
    resultado_imagenes: ResultadoImagenesPDF,
    ruta_destino
):
    """
    Genera un Word editable con textos e imagenes.

    No incorpora las imagenes de paginas procesadas
    mediante OCR completo, para evitar repetir
    visualmente la pagina escaneada.

    Retorna la ruta del documento generado.
    """

    destino = Path(ruta_destino)

    # 1. Validar la ubicacion de salida.
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

    # 2. Comprobar consistencia entre resultados.
    if (
        resultado_ocr.total_paginas
        != resultado_imagenes.total_paginas
    ):
        raise ValueError(
            "Los resultados corresponden a documentos "
            "con distinta cantidad de paginas."
        )

    if (
        resultado_ocr.total_paginas
        != len(resultado_ocr.paginas)
    ):
        raise ValueError(
            "La cantidad de paginas OCR es inconsistente."
        )

    numeros_paginas = tuple(
        pagina.numero_pagina
        for pagina in resultado_ocr.paginas
    )

    if numeros_paginas != tuple(
        range(1, resultado_ocr.total_paginas + 1)
    ):
        raise ValueError(
            "Las paginas OCR no estan en orden."
        )

    # 3. Organizar las imagenes por pagina.
    imagenes_por_pagina = {}

    for imagen in resultado_imagenes.imagenes:

        if not 1 <= imagen.numero_pagina <= resultado_ocr.total_paginas:
            raise ValueError(
                "Una imagen tiene un numero de pagina invalido."
            )

        imagenes_por_pagina.setdefault(
            imagen.numero_pagina, []
        ).append(imagen)

    # 4. Construir el Word.
    documento_word = Document()

    for indice, pagina in enumerate(resultado_ocr.paginas):

        if indice > 0:
            documento_word.add_page_break()

        # Incorporar el texto editable.
        for linea in pagina.texto.splitlines():
            documento_word.add_paragraph(linea)

        # No repetir una pagina escaneada completa.
        if pagina.metodo == "ocr_completo":
            continue

        imagenes = imagenes_por_pagina.get(
            pagina.numero_pagina, []
        )

        for imagen in imagenes:

            if imagen.formato.lower() not in (
                "png", "jpeg", "jpg"
            ):
                raise ValueError(
                    "Formato de imagen no compatible "
                    f"con esta exportacion: {imagen.formato}"
                )

            # La imagen ocupa como maximo un ancho
            # aproximado de 5,8 pulgadas.
            ancho_original = (
                imagen.coordenadas[2]
                - imagen.coordenadas[0]
            )

            ancho_pulgadas = min(
                ancho_original / 72,
                5.8
            )

            if ancho_pulgadas <= 0:
                raise ValueError(
                    "La imagen tiene dimensiones invalidas."
                )

            documento_word.add_picture(
                BytesIO(imagen.datos),
                width=Inches(ancho_pulgadas)
            )

    # 5. Guardar primero en un archivo temporal.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_visual_",
        suffix=".docx",
        dir=destino.parent
    )

    os.close(descriptor)
    temporal = Path(ruta_temporal)

    try:
        documento_word.save(str(temporal))

        # Validacion reutilizada del conversor.
        validar_documento_word(temporal)

        # Publicar sin reemplazar archivos existentes.
        os.link(temporal, destino)

        return str(destino)

    finally:
        temporal.unlink(missing_ok=True)
