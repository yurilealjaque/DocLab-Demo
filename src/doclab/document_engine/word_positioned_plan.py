
"""
Plan de reconstruccion Word con texto OCR posicionado.

Combina:
- Resultados de inspeccion y OCR por pagina.
- Bloques de texto e imagenes del PDF.
- Fragmentos de texto con coordenadas OCR.

No genera documentos Word.
"""

from doclab.document_engine.ocr_document import (
    ResultadoDocumentoOCR
)

from doclab.document_engine.ocr_text_blocks import (
    ResultadoTextoPosicionado
)

from doclab.document_engine.pdf_layout import (
    ResultadoEstructuraPDF
)

from doclab.document_engine.word_layout_plan import (
    ElementoPlanWord,
    ResultadoPlanWord
)


def crear_plan_word_posicionado(
    resultado_ocr,
    resultado_estructura,
    resultados_posicionados
):
    """
    Construye un plan de elementos ordenados.

    digital:
        Utiliza los bloques originales del PDF.

    ocr_parcial:
        Utiliza los fragmentos OCR posicionados
        y conserva los bloques de imagen.

    ocr_completo:
        Utiliza solamente el texto OCR posicionado.

    vacia:
        No incorpora elementos.

    resultados_posicionados:
        Coleccion de ResultadoTextoPosicionado.
        Se exige uno por cada pagina que usa OCR.
    """

    # 1. Comprobar los tipos de datos.
    if not isinstance(
        resultado_ocr,
        ResultadoDocumentoOCR
    ):
        raise TypeError(
            "Se esperaba un ResultadoDocumentoOCR."
        )

    if not isinstance(
        resultado_estructura,
        ResultadoEstructuraPDF
    ):
        raise TypeError(
            "Se esperaba un ResultadoEstructuraPDF."
        )

    total = resultado_ocr.total_paginas

    # 2. Comprobar la consistencia.
    if total < 1:
        raise ValueError(
            "El documento debe contener paginas."
        )

    if total != resultado_estructura.total_paginas:
        raise ValueError(
            "Los resultados tienen distinta "
            "cantidad de paginas."
        )

    if len(resultado_ocr.paginas) != total:
        raise ValueError(
            "La cantidad de paginas OCR es invalida."
        )

    numeros = tuple(
        pagina.numero_pagina
        for pagina in resultado_ocr.paginas
    )

    if numeros != tuple(range(1, total + 1)):
        raise ValueError(
            "Las paginas OCR no son consecutivas."
        )

    # 3. Indexar resultados posicionados por pagina.
    posicionados = {}

    for resultado in resultados_posicionados:

        if not isinstance(
            resultado,
            ResultadoTextoPosicionado
        ):
            raise TypeError(
                "Resultado posicionado invalido."
            )

        numero = resultado.numero_pagina

        if not 1 <= numero <= total:
            raise ValueError(
                "Resultado posicionado fuera de rango."
            )

        if numero in posicionados:
            raise ValueError(
                "Existe mas de un resultado "
                "posicionado para la misma pagina."
            )

        if any(
            fragmento.numero_pagina != numero
            for fragmento in resultado.fragmentos
        ):
            raise ValueError(
                "Un fragmento pertenece a otra pagina."
            )

        posicionados[numero] = resultado

    # 4. Comprobar los bloques estructurales.
    bloques_por_pagina = {
        numero: []
        for numero in range(1, total + 1)
    }

    for bloque in resultado_estructura.bloques:

        if bloque.numero_pagina not in bloques_por_pagina:
            raise ValueError(
                "Bloque estructural fuera de rango."
            )

        bloques_por_pagina[
            bloque.numero_pagina
        ].append(bloque)

    elementos = []

    # 5. Procesar las paginas en orden.
    for pagina in resultado_ocr.paginas:

        numero = pagina.numero_pagina
        metodo = pagina.metodo

        bloques = bloques_por_pagina[numero]
        elementos_pagina = []

        if metodo == "vacia":
            continue

        # Caso A: texto digital.
        if metodo == "digital":

            for bloque in bloques:

                if bloque.tipo not in ("texto", "imagen"):
                    continue

                elementos_pagina.append(
                    ElementoPlanWord(
                        numero_pagina=numero,
                        tipo=bloque.tipo,
                        texto=bloque.texto,
                        coordenadas=bloque.coordenadas
                    )
                )

        # Caso B: OCR parcial o completo.
        elif metodo in ("ocr_parcial", "ocr_completo"):

            if numero not in posicionados:
                raise ValueError(
                    "Faltan fragmentos OCR "
                    f"de la pagina {numero}."
                )

            resultado_pagina = posicionados[numero]

            # Recuperar los fragmentos digital y OCR
            # sin volver a agregar los bloques de
            # texto digital desde pdf_layout.py.
            for fragmento in resultado_pagina.fragmentos:

                elementos_pagina.append(
                    ElementoPlanWord(
                        numero_pagina=numero,
                        tipo="texto",
                        texto=fragmento.texto,
                        coordenadas=fragmento.coordenadas
                    )
                )

            # En las paginas mixtas conservamos
            # las imagenes originales.
            if metodo == "ocr_parcial":

                for bloque in bloques:

                    if bloque.tipo == "imagen":

                        elementos_pagina.append(
                            ElementoPlanWord(
                                numero_pagina=numero,
                                tipo="imagen",
                                texto="",
                                coordenadas=bloque.coordenadas
                            )
                        )

        else:
            raise ValueError(
                f"Metodo desconocido: {metodo}"
            )

        # 6. Ordenar los elementos de esta pagina.
        elementos_pagina.sort(
            key=lambda elemento: (
                elemento.coordenadas[1],
                elemento.coordenadas[0]
            )
        )

        elementos.extend(elementos_pagina)

    # 7. Construir el resultado.
    return ResultadoPlanWord(
        total_paginas=total,
        elementos=tuple(elementos)
    )
