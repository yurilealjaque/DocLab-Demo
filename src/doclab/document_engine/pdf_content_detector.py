
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf

from doclab.document_engine.image_coverage import (
    es_posible_escaneo
)


@dataclass(frozen=True)
class ResultadoInspeccionPDF:
    total_paginas: int
    paginas_con_texto: tuple[int, ...]
    paginas_sin_texto: tuple[int, ...]
    clasificacion: str

    # Informacion de imagenes.
    paginas_con_imagenes: tuple[int, ...] = ()
    paginas_con_texto_e_imagenes: tuple[int, ...] = ()
    total_imagenes: int = 0

    # Nuevo: paginas candidatas a escaneo.
    paginas_posibles_escaneos: tuple[int, ...] = ()


def inspeccionar_contenido_pdf(ruta_archivo):
    """
    Inspecciona el contenido de un documento PDF.

    Detecta:
    - Texto extraible.
    - Imagenes.
    - Paginas con texto e imagenes.
    - Posibles paginas escaneadas sin texto extraible.

    No ejecuta OCR.
    """

    ruta = Path(ruta_archivo)

    # 1. Validar el documento.
    validar_pdf(ruta)

    # 2. Preparar los resultados.
    paginas_con_texto = []
    paginas_sin_texto = []
    paginas_con_imagenes = []
    paginas_con_texto_e_imagenes = []
    paginas_posibles_escaneos = []

    total_imagenes = 0

    # 3. Abrir y recorrer el PDF.
    with pymupdf.open(
        str(ruta),
        filetype="pdf"
    ) as documento:

        for numero, pagina in enumerate(
            documento,
            start=1
        ):

            # 4. Comprobar texto extraible.
            texto = pagina.get_text("text").strip()

            tiene_texto = bool(texto)

            if tiene_texto:
                paginas_con_texto.append(numero)
            else:
                paginas_sin_texto.append(numero)

            # 5. Detectar imagenes.
            imagenes = pagina.get_image_info()

            tiene_imagenes = len(imagenes) > 0

            total_imagenes += len(imagenes)

            if tiene_imagenes:
                paginas_con_imagenes.append(numero)

            # 6. Detectar texto e imagenes juntos.
            if tiene_texto and tiene_imagenes:
                paginas_con_texto_e_imagenes.append(numero)

            # 7. Identificar posibles escaneos.
            if not tiene_texto and tiene_imagenes:

                if es_posible_escaneo(
                    pagina,
                    umbral=0.80
                ):
                    paginas_posibles_escaneos.append(
                        numero
                    )

    # 8. Clasificar el texto del documento.
    if not paginas_sin_texto:
        clasificacion = "con_texto"

    elif not paginas_con_texto:
        clasificacion = "sin_texto"

    else:
        clasificacion = "mixto"

    # 9. Entregar el resultado.
    return ResultadoInspeccionPDF(
        total_paginas=(
            len(paginas_con_texto)
            + len(paginas_sin_texto)
        ),
        paginas_con_texto=tuple(paginas_con_texto),
        paginas_sin_texto=tuple(paginas_sin_texto),
        clasificacion=clasificacion,
        paginas_con_imagenes=tuple(paginas_con_imagenes),
        paginas_con_texto_e_imagenes=tuple(
            paginas_con_texto_e_imagenes
        ),
        total_imagenes=total_imagenes,
        paginas_posibles_escaneos=tuple(
            paginas_posibles_escaneos
        )
    )
