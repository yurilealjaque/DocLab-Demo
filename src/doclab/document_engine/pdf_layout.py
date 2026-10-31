
"""
Analisis de estructura visual de documentos PDF.

Obtiene bloques de texto e imagenes, junto con
su posicion aproximada dentro de cada pagina.

No modifica documentos ni ejecuta OCR.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf


@dataclass(frozen=True)
class BloquePDF:
    numero_pagina: int
    tipo: str
    coordenadas: tuple[float, float, float, float]
    texto: str = ""


@dataclass(frozen=True)
class ResultadoEstructuraPDF:
    total_paginas: int
    bloques: tuple[BloquePDF, ...]


def analizar_estructura_pdf(ruta_archivo):
    """
    Identifica bloques de texto e imagenes.

    Las coordenadas representan:
    (x0, y0, x1, y1).

    Retorna un ResultadoEstructuraPDF.
    """

    ruta = Path(ruta_archivo)

    # 1. Reutilizar nuestro validador.
    validar_pdf(ruta)

    bloques_encontrados = []

    # 2. Abrir y recorrer el documento.
    with pymupdf.open(
        str(ruta),
        filetype="pdf"
    ) as documento:

        for numero, pagina in enumerate(
            documento,
            start=1
        ):

            # 3. Obtener la estructura de la pagina.
            estructura = pagina.get_text("dict")

            for bloque in estructura["blocks"]:

                tipo_bloque = bloque["type"]

                coordenadas = tuple(
                    bloque["bbox"]
                )

                # 4. Procesar los bloques de texto.
                if tipo_bloque == 0:

                    lineas = []

                    for linea in bloque["lines"]:

                        fragmentos = []

                        for fragmento in linea["spans"]:
                            fragmentos.append(
                                fragmento["text"]
                            )

                        lineas.append(
                            "".join(fragmentos)
                        )

                    texto = "\n".join(lineas).strip()

                    if texto:
                        bloques_encontrados.append(
                            BloquePDF(
                                numero_pagina=numero,
                                tipo="texto",
                                coordenadas=coordenadas,
                                texto=texto
                            )
                        )

                # 5. Procesar los bloques de imagen.
                elif tipo_bloque == 1:

                    bloques_encontrados.append(
                        BloquePDF(
                            numero_pagina=numero,
                            tipo="imagen",
                            coordenadas=coordenadas
                        )
                    )

    # 6. Devolver el resultado.
    return ResultadoEstructuraPDF(
        total_paginas=numero,
        bloques=tuple(bloques_encontrados)
    )
