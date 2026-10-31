
"""
Extraccion de imagenes de documentos PDF.

Recupera el contenido binario y la ubicacion
de las imagenes presentes en cada pagina.

No modifica el PDF original ni ejecuta OCR.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import (
    validar_pdf
)


@dataclass(frozen=True)
class ImagenExtraidaPDF:
    numero_pagina: int
    coordenadas: tuple[float, float, float, float]
    formato: str
    datos: bytes


@dataclass(frozen=True)
class ResultadoImagenesPDF:
    total_paginas: int
    imagenes: tuple[ImagenExtraidaPDF, ...]


def extraer_imagenes_pdf(ruta_archivo):
    """
    Extrae las imagenes mostradas en un PDF.

    Devuelve:
    - Numero de pagina.
    - Coordenadas de la imagen.
    - Formato original.
    - Datos binarios.

    No guarda archivos en el disco.
    """

    ruta = Path(ruta_archivo)

    # 1. Reutilizar el validador existente.
    validar_pdf(ruta)

    imagenes_extraidas = []

    # 2. Abrir el PDF.
    with pymupdf.open(
        str(ruta),
        filetype="pdf"
    ) as documento:

        total_paginas = documento.page_count

        # 3. Recorrer sus paginas.
        for numero, pagina in enumerate(
            documento,
            start=1
        ):

            # Obtener bloques de contenido.
            estructura = pagina.get_text("dict")

            for bloque in estructura["blocks"]:

                # El tipo 1 representa una imagen.
                if bloque["type"] != 1:
                    continue

                # 4. Recuperar sus propiedades.
                coordenadas = tuple(bloque["bbox"])

                formato = bloque["ext"]

                datos = bloque["image"]

                # 5. Registrar la imagen.
                imagenes_extraidas.append(
                    ImagenExtraidaPDF(
                        numero_pagina=numero,
                        coordenadas=coordenadas,
                        formato=formato,
                        datos=datos
                    )
                )

    # 6. Devolver el resultado completo.
    return ResultadoImagenesPDF(
        total_paginas=total_paginas,
        imagenes=tuple(imagenes_extraidas)
    )
