
"""
Ordenamiento geometrico de bloques de un PDF.

Organiza bloques de texto e imagenes por:
1. Numero de pagina.
2. Posicion vertical (de arriba hacia abajo).
3. Posicion horizontal (de izquierda a derecha).

No modifica los bloques originales.
No ejecuta OCR ni genera documentos Word.
"""

from doclab.document_engine.pdf_layout import (
    ResultadoEstructuraPDF
)


def ordenar_bloques_por_posicion(resultado_estructura):
    """
    Devuelve un nuevo ResultadoEstructuraPDF
    con los bloques ordenados geometricamente.

    Es una aproximacion adecuada para paginas
    de estructura sencilla, no un detector
    completo del orden semantico de lectura.
    """

    if not isinstance(
        resultado_estructura,
        ResultadoEstructuraPDF
    ):
        raise TypeError(
            "Se esperaba un ResultadoEstructuraPDF."
        )

    if resultado_estructura.total_paginas < 1:
        raise ValueError(
            "El documento debe contener paginas."
        )

    # Validar que cada bloque pertenezca
    # a una pagina del documento.
    for bloque in resultado_estructura.bloques:

        if not (
            1 <= bloque.numero_pagina
            <= resultado_estructura.total_paginas
        ):
            raise ValueError(
                "Se encontro un bloque con pagina invalida."
            )

    # Ordenar sin modificar la tupla original.
    bloques_ordenados = sorted(
        resultado_estructura.bloques,
        key=lambda bloque: (
            bloque.numero_pagina,
            bloque.coordenadas[1],
            bloque.coordenadas[0]
        )
    )

    return ResultadoEstructuraPDF(
        total_paginas=resultado_estructura.total_paginas,
        bloques=tuple(bloques_ordenados)
    )
