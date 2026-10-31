
"""
Extraccion de texto con coordenadas mediante OCR.

Recupera fragmentos de texto de una pagina PDF
y distingue su procedencia digital u OCR.

No modifica el PDF ni genera documentos Word.
"""

from dataclasses import dataclass

import pymupdf

from doclab.document_engine.pdf_validator import (
    validar_pdf
)

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr,
    ErrorReconocimientoOCR
)


@dataclass(frozen=True)
class FragmentoTextoPDF:
    numero_pagina: int
    texto: str
    coordenadas: tuple[float, float, float, float]
    origen: str


@dataclass(frozen=True)
class ResultadoTextoPosicionado:
    numero_pagina: int
    fragmentos: tuple[FragmentoTextoPDF, ...]


def extraer_texto_posicionado(
    ruta_archivo,
    numero_pagina,
    idioma="spa+eng",
    dpi=300,
    completo=False,
    carpeta_tessdata=None
):
    """
    Obtiene fragmentos de texto con coordenadas.

    completo=False:
        Conserva el texto digital y reconoce
        texto adicional mediante OCR.

    completo=True:
        Reconoce toda la pagina mediante OCR.

    Los fragmentos se obtienen desde las
    lineas y los spans de PyMuPDF.
    """

    # 1. Validar los parametros de entrada.
    if (
        isinstance(numero_pagina, bool)
        or not isinstance(numero_pagina, int)
        or numero_pagina < 1
    ):
        raise ValueError(
            "El numero de pagina debe ser un entero positivo."
        )

    if (
        isinstance(dpi, bool)
        or not isinstance(dpi, int)
        or not 72 <= dpi <= 600
    ):
        raise ValueError(
            "La resolucion OCR debe estar entre 72 y 600 DPI."
        )

    # 2. Validar el documento.
    total_paginas = validar_pdf(ruta_archivo)

    if numero_pagina > total_paginas:
        raise ValueError(
            "La pagina solicitada no existe."
        )

    # 3. Verificar los modelos locales.
    carpeta = verificar_recursos_ocr(
        carpeta_tessdata=carpeta_tessdata,
        idioma=idioma
    )

    fragmentos = []

    try:
        # 4. Abrir el PDF.
        with pymupdf.open(
            str(ruta_archivo),
            filetype="pdf"
        ) as documento:

            pagina = documento.load_page(
                numero_pagina - 1
            )

            # 5. Ejecutar OCR y conservar su TextPage.
            pagina_ocr = pagina.get_textpage_ocr(
                language=idioma,
                dpi=dpi,
                full=completo,
                tessdata=str(carpeta)
            )

            # 6. Obtener los bloques con coordenadas.
            estructura = pagina.get_text(
                "dict",
                textpage=pagina_ocr
            )

            for bloque in estructura["blocks"]:

                # Ignorar bloques de imagen.
                if bloque["type"] != 0:
                    continue

                for linea in bloque["lines"]:

                    for fragmento in linea["spans"]:

                        texto = fragmento["text"].strip()

                        if not texto:
                            continue

                        # 7. Identificar el origen.
                        nombre_fuente = fragmento[
                            "font"
                        ].lower()

                        if "glyphlessfont" in nombre_fuente:
                            origen = "ocr"
                        else:
                            origen = "digital"

                        # 8. Registrar las coordenadas.
                        coordenadas = tuple(
                            fragmento["bbox"]
                        )

                        fragmentos.append(
                            FragmentoTextoPDF(
                                numero_pagina=numero_pagina,
                                texto=texto,
                                coordenadas=coordenadas,
                                origen=origen
                            )
                        )

    except Exception as error:
        raise ErrorReconocimientoOCR(
            "No fue posible extraer el texto "
            "posicionado de la pagina."
        ) from error

    return ResultadoTextoPosicionado(
        numero_pagina=numero_pagina,
        fragmentos=tuple(fragmentos)
    )
