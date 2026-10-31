
"""
Plan de reconstruccion de documentos Word.

Combina la estructura geometrica del PDF
con los resultados del reconocimiento OCR.

No genera archivos Word ni modifica el PDF.
"""

from dataclasses import dataclass

from doclab.document_engine.pdf_layout import (
    BloquePDF,
    ResultadoEstructuraPDF
)

from doclab.document_engine.pdf_reading_order import (
    ordenar_bloques_por_posicion
)

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR
)


@dataclass(frozen=True)
class ElementoPlanWord:
    numero_pagina: int
    tipo: str
    texto: str
    coordenadas: tuple[float, float, float, float] | None


@dataclass(frozen=True)
class ResultadoPlanWord:
    total_paginas: int
    elementos: tuple[ElementoPlanWord, ...]


def crear_plan_word(resultado_ocr, resultado_estructura):
    """
    Crea una secuencia de elementos para exportar a Word.

    Pagina digital:
        Ordena sus bloques originales.

    Pagina con OCR parcial:
        Conserva el texto OCR una sola vez y
        mantiene los bloques de imagen.

    Pagina con OCR completo:
        Usa solo el texto reconocido.

    Pagina vacia:
        No agrega elementos.

    La posicion del texto OCR parcial es
    aproximada porque aun no disponemos
    de coordenadas para sus palabras.
    """

    if not isinstance(resultado_ocr, ResultadoDocumentoOCR):
        raise TypeError("Resultado OCR invalido.")

    if not isinstance(
        resultado_estructura,
        ResultadoEstructuraPDF
    ):
        raise TypeError("Resultado de estructura invalido.")

    total = resultado_ocr.total_paginas

    if total != resultado_estructura.total_paginas:
        raise ValueError(
            "Los resultados tienen distinta cantidad de paginas."
        )

    if total < 1 or len(resultado_ocr.paginas) != total:
        raise ValueError(
            "El resultado OCR tiene una cantidad de paginas invalida."
        )

    numeros = tuple(
        pagina.numero_pagina for pagina in resultado_ocr.paginas
    )

    if numeros != tuple(range(1, total + 1)):
        raise ValueError(
            "Las paginas OCR deben estar ordenadas consecutivamente."
        )

    estructura_ordenada = ordenar_bloques_por_posicion(
        resultado_estructura
    )

    elementos = []

    for pagina_ocr in resultado_ocr.paginas:
        numero = pagina_ocr.numero_pagina

        bloques = [
            bloque
            for bloque in estructura_ordenada.bloques
            if bloque.numero_pagina == numero
        ]

        if pagina_ocr.metodo == "vacia":
            continue

        if pagina_ocr.metodo == "ocr_completo":
            if pagina_ocr.texto.strip():
                elementos.append(
                    ElementoPlanWord(
                        numero_pagina=numero,
                        tipo="texto",
                        texto=pagina_ocr.texto,
                        coordenadas=None
                    )
                )

            continue

        if pagina_ocr.metodo == "digital":
            for bloque in bloques:
                elementos.append(
                    ElementoPlanWord(
                        numero_pagina=numero,
                        tipo=bloque.tipo,
                        texto=bloque.texto,
                        coordenadas=bloque.coordenadas
                    )
                )

            continue

        if pagina_ocr.metodo == "ocr_parcial":
            # El texto completo del OCR parcial contiene
            # tambien el texto digital de la pagina.
            # Por eso NO agregamos nuevamente los
            # bloques digitales de la estructura.

            bloques_imagen = [
                bloque for bloque in bloques
                if bloque.tipo == "imagen"
            ]

            bloques_texto = [
                bloque for bloque in bloques
                if bloque.tipo == "texto"
            ]

            bloques_plan = list(bloques_imagen)

            if pagina_ocr.texto.strip():
                if bloques_texto:
                    posicion = bloques_texto[0].coordenadas
                elif bloques_imagen:
                    posicion = bloques_imagen[0].coordenadas
                else:
                    posicion = (0.0, 0.0, 0.0, 0.0)

                bloques_plan.append(
                    BloquePDF(
                        numero_pagina=numero,
                        tipo="texto",
                        coordenadas=posicion,
                        texto=pagina_ocr.texto
                    )
                )

            orden_parcial = ordenar_bloques_por_posicion(
                ResultadoEstructuraPDF(
                    total_paginas=total,
                    bloques=tuple(bloques_plan)
                )
            )

            for bloque in orden_parcial.bloques:
                elementos.append(
                    ElementoPlanWord(
                        numero_pagina=numero,
                        tipo=bloque.tipo,
                        texto=bloque.texto,
                        coordenadas=bloque.coordenadas
                    )
                )

            continue

        raise ValueError(
            f"Metodo de procesamiento desconocido: {pagina_ocr.metodo}"
        )

    return ResultadoPlanWord(
        total_paginas=total,
        elementos=tuple(elementos)
    )
