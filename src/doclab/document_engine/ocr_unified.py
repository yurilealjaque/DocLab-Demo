
"""
Procesamiento OCR unificado de DocLab.

Obtiene el texto y sus coordenadas utilizando
un unico reconocimiento OCR por pagina.

Conserva las estructuras de resultados existentes
para mantener compatibilidad con otros modulos.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr,
    ErrorReconocimientoOCR
)

from doclab.document_engine.ocr_document import (
    ResultadoPaginaOCR,
    ResultadoDocumentoOCR
)

from doclab.document_engine.ocr_text_blocks import (
    FragmentoTextoPDF,
    ResultadoTextoPosicionado
)


@dataclass(frozen=True)
class ResultadoOCRUnificado:
    documento: ResultadoDocumentoOCR
    paginas_posicionadas: tuple[
        ResultadoTextoPosicionado, ...
    ]


def procesar_ocr_unificado(
    ruta_archivo,
    idioma="spa+eng",
    dpi=300,
    carpeta_tessdata=None
):
    """
    Procesa un PDF completo.

    En paginas digitales:
        Extrae texto sin ejecutar OCR.

    En paginas con imagenes:
        Ejecuta OCR una sola vez y reutiliza
        su TextPage para recuperar texto
        y coordenadas.

    Retorna un ResultadoOCRUnificado.
    """

    # 1. Validar la resolucion.
    if (
        isinstance(dpi, bool)
        or not isinstance(dpi, int)
        or not 72 <= dpi <= 600
    ):
        raise ValueError(
            "La resolucion OCR debe estar entre 72 y 600 DPI."
        )

    ruta = Path(ruta_archivo)

    # 2. Inspeccionar el documento existente.
    inspeccion = inspeccionar_contenido_pdf(ruta)

    paginas_con_texto = set(
        inspeccion.paginas_con_texto
    )

    paginas_con_imagenes = set(
        inspeccion.paginas_con_imagenes
    )

    resultados_paginas = []
    resultados_posicionados = []

    # Los recursos solo se verifican si
    # encontramos una pagina que necesita OCR.
    carpeta = None

    # 3. Abrir el documento una vez para procesarlo.
    with pymupdf.open(
        str(ruta),
        filetype="pdf"
    ) as documento:

        for numero, pagina in enumerate(
            documento,
            start=1
        ):

            tiene_texto = numero in paginas_con_texto
            tiene_imagenes = numero in paginas_con_imagenes

            # A. Pagina digital sin imagenes.
            if tiene_texto and not tiene_imagenes:

                texto = pagina.get_text("text").strip()
                metodo = "digital"

            # B. Pagina vacia.
            elif not tiene_texto and not tiene_imagenes:

                texto = ""
                metodo = "vacia"

            # C. Pagina con imagenes.
            else:

                if tiene_texto:
                    metodo = "ocr_parcial"
                    completo = False
                else:
                    metodo = "ocr_completo"
                    completo = True

                if carpeta is None:
                    carpeta = verificar_recursos_ocr(
                        carpeta_tessdata=carpeta_tessdata,
                        idioma=idioma
                    )

                try:
                    # Ejecutar OCR una sola vez.
                    pagina_ocr = pagina.get_textpage_ocr(
                        language=idioma,
                        dpi=dpi,
                        full=completo,
                        tessdata=str(carpeta)
                    )

                    # Reutilizar el TextPage para texto.
                    texto = pagina.get_text(
                        "text",
                        textpage=pagina_ocr
                    ).strip()

                    # Reutilizarlo para coordenadas.
                    estructura = pagina.get_text(
                        "dict",
                        textpage=pagina_ocr
                    )

                    fragmentos = []

                    for bloque in estructura["blocks"]:

                        if bloque["type"] != 0:
                            continue

                        for linea in bloque["lines"]:

                            for span in linea["spans"]:

                                contenido = span[
                                    "text"
                                ].strip()

                                if not contenido:
                                    continue

                                fuente = span[
                                    "font"
                                ].lower()

                                if "glyphlessfont" in fuente:
                                    origen = "ocr"
                                else:
                                    origen = "digital"

                                fragmentos.append(
                                    FragmentoTextoPDF(
                                        numero_pagina=numero,
                                        texto=contenido,
                                        coordenadas=tuple(
                                            span["bbox"]
                                        ),
                                        origen=origen
                                    )
                                )

                except Exception as error:
                    raise ErrorReconocimientoOCR(
                        "Fallo el procesamiento OCR "
                        f"de la pagina {numero}."
                    ) from error

                resultados_posicionados.append(
                    ResultadoTextoPosicionado(
                        numero_pagina=numero,
                        fragmentos=tuple(fragmentos)
                    )
                )

            # 4. Registrar el resultado de la pagina.
            resultados_paginas.append(
                ResultadoPaginaOCR(
                    numero_pagina=numero,
                    texto=texto,
                    metodo=metodo
                )
            )

    # 5. Construir resultados compatibles.
    resultado_documento = ResultadoDocumentoOCR(
        total_paginas=inspeccion.total_paginas,
        paginas=tuple(resultados_paginas)
    )

    return ResultadoOCRUnificado(
        documento=resultado_documento,
        paginas_posicionadas=tuple(
            resultados_posicionados
        )
    )
