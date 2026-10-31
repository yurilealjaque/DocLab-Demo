
"""
Procesamiento OCR de documentos PDF completos.

Selecciona la estrategia de extraccion de texto
para cada pagina segun su contenido.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)

from doclab.document_engine.ocr_engine import (
    reconocer_texto_pagina
)


@dataclass(frozen=True)
class ResultadoPaginaOCR:
    numero_pagina: int
    texto: str
    metodo: str


@dataclass(frozen=True)
class ResultadoDocumentoOCR:
    total_paginas: int
    paginas: tuple[ResultadoPaginaOCR, ...]


def procesar_documento_ocr(
    ruta_archivo,
    idioma="spa+eng",
    dpi=300,
    carpeta_tessdata=None
):
    """
    Procesa todas las paginas de un PDF.

    Metodos:
    - digital: extraccion directa de texto.
    - ocr_completo: imagen sin texto extraible.
    - ocr_parcial: texto digital e imagenes.
    - vacia: pagina sin texto ni imagenes.

    Retorna un ResultadoDocumentoOCR.
    """

    ruta = Path(ruta_archivo)

    # 1. Inspeccionar el documento completo.
    inspeccion = inspeccionar_contenido_pdf(ruta)

    paginas_con_texto = set(
        inspeccion.paginas_con_texto
    )

    paginas_con_imagenes = set(
        inspeccion.paginas_con_imagenes
    )

    resultados = []

    # 2. Abrir el PDF para extraer texto digital.
    with pymupdf.open(
        str(ruta),
        filetype="pdf"
    ) as documento:

        # 3. Procesar cada pagina.
        for numero_pagina in range(
            1,
            inspeccion.total_paginas + 1
        ):

            tiene_texto = (
                numero_pagina in paginas_con_texto
            )

            tiene_imagenes = (
                numero_pagina in paginas_con_imagenes
            )

            # Caso A: pagina con texto e imagenes.
            if tiene_texto and tiene_imagenes:

                resultado = reconocer_texto_pagina(
                    ruta_archivo=ruta,
                    numero_pagina=numero_pagina,
                    idioma=idioma,
                    dpi=dpi,
                    completo=False,
                    carpeta_tessdata=carpeta_tessdata
                )

                texto = resultado.texto
                metodo = "ocr_parcial"

            # Caso B: pagina con imagenes, sin texto.
            elif tiene_imagenes:

                resultado = reconocer_texto_pagina(
                    ruta_archivo=ruta,
                    numero_pagina=numero_pagina,
                    idioma=idioma,
                    dpi=dpi,
                    completo=True,
                    carpeta_tessdata=carpeta_tessdata
                )

                texto = resultado.texto
                metodo = "ocr_completo"

            # Caso C: pagina con texto digital.
            elif tiene_texto:

                pagina = documento.load_page(
                    numero_pagina - 1
                )

                texto = pagina.get_text("text").strip()
                metodo = "digital"

            # Caso D: pagina vacia.
            else:

                texto = ""
                metodo = "vacia"

            # 4. Registrar el resultado.
            resultados.append(
                ResultadoPaginaOCR(
                    numero_pagina=numero_pagina,
                    texto=texto,
                    metodo=metodo
                )
            )

    # 5. Devolver todos los resultados.
    return ResultadoDocumentoOCR(
        total_paginas=inspeccion.total_paginas,
        paginas=tuple(resultados)
    )
