
"""
Exportador Word basado en un plan de reconstruccion.

Inserta texto e imagenes en el orden calculado
por word_layout_plan.py.

No reconstruye posiciones absolutas del PDF.
"""

import os
import tempfile

from io import BytesIO
from pathlib import Path

from docx import Document
from docx.shared import Inches

from doclab.document_engine.word_layout_plan import (
    ResultadoPlanWord
)

from doclab.document_engine.pdf_image_extractor import (
    ResultadoImagenesPDF
)

from doclab.document_engine.pdf_to_word import (
    validar_documento_word
)


def buscar_imagen_correspondiente(
    elemento,
    imagenes,
    indices_utilizados,
    tolerancia=1.0
):
    """
    Busca una imagen por pagina y coordenadas.

    Cada aparicion de imagen puede utilizarse
    solo una vez.
    """

    if elemento.coordenadas is None:
        raise ValueError(
            "El bloque de imagen no tiene coordenadas."
        )

    for indice, imagen in enumerate(imagenes):

        if indice in indices_utilizados:
            continue

        if imagen.numero_pagina != elemento.numero_pagina:
            continue

        diferencias = [
            abs(valor_elemento - valor_imagen)
            for valor_elemento, valor_imagen in zip(
                elemento.coordenadas,
                imagen.coordenadas
            )
        ]

        if all(
            diferencia <= tolerancia
            for diferencia in diferencias
        ):
            indices_utilizados.add(indice)
            return imagen

    raise ValueError(
        "No se encontro una imagen correspondiente "
        f"al bloque de la pagina {elemento.numero_pagina}."
    )


def exportar_plan_a_word(
    resultado_plan: ResultadoPlanWord,
    resultado_imagenes: ResultadoImagenesPDF,
    ruta_destino
):
    """
    Genera un DOCX siguiendo el orden del plan.

    Incluye:
    - Texto editable.
    - Imagenes en linea.
    - Saltos entre paginas originales.

    No sobrescribe documentos existentes.
    """

    destino = Path(ruta_destino)

    # 1. Validar la salida.
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

    # 2. Validar los resultados recibidos.
    total = resultado_plan.total_paginas

    if total < 1:
        raise ValueError(
            "El documento debe contener al menos una pagina."
        )

    if total != resultado_imagenes.total_paginas:
        raise ValueError(
            "El plan y las imagenes tienen distinta "
            "cantidad de paginas."
        )

    elementos = resultado_plan.elementos
    imagenes = resultado_imagenes.imagenes

    pagina_anterior = 0

    for elemento in elementos:

        if not 1 <= elemento.numero_pagina <= total:
            raise ValueError(
                "Un elemento tiene una pagina invalida."
            )

        if elemento.numero_pagina < pagina_anterior:
            raise ValueError(
                "Los elementos no estan ordenados por pagina."
            )

        if elemento.tipo not in ("texto", "imagen"):
            raise ValueError(
                f"Tipo de elemento desconocido: {elemento.tipo}"
            )

        pagina_anterior = elemento.numero_pagina

    # 3. Asociar las imagenes antes de crear el DOCX.
    indices_utilizados = set()
    imagenes_asociadas = {}

    for indice, elemento in enumerate(elementos):

        if elemento.tipo != "imagen":
            continue

        imagen = buscar_imagen_correspondiente(
            elemento,
            imagenes,
            indices_utilizados
        )

        if imagen.formato.lower() not in (
            "png", "jpg", "jpeg"
        ):
            raise ValueError(
                "Formato de imagen no compatible: "
                f"{imagen.formato}"
            )

        ancho = (
            elemento.coordenadas[2]
            - elemento.coordenadas[0]
        )

        if ancho <= 0:
            raise ValueError(
                "La imagen tiene un ancho invalido."
            )

        imagenes_asociadas[indice] = imagen

    # 4. Crear el documento.
    documento_word = Document()
    numero_pagina_actual = 1

    for indice, elemento in enumerate(elementos):

        # Respetar los cambios de pagina,
        # incluso cuando hay paginas vacias.
        while numero_pagina_actual < elemento.numero_pagina:
            documento_word.add_page_break()
            numero_pagina_actual += 1

        if elemento.tipo == "texto":

            for linea in elemento.texto.splitlines():
                documento_word.add_paragraph(linea)

        elif elemento.tipo == "imagen":

            imagen = imagenes_asociadas[indice]

            ancho_puntos = (
                elemento.coordenadas[2]
                - elemento.coordenadas[0]
            )

            ancho_pulgadas = min(
                ancho_puntos / 72,
                5.8
            )

            documento_word.add_picture(
                BytesIO(imagen.datos),
                width=Inches(ancho_pulgadas)
            )

    # Conservar los cambios hasta la ultima pagina,
    # aunque las paginas finales esten vacias.
    while numero_pagina_actual < total:
        documento_word.add_page_break()
        numero_pagina_actual += 1

    # 5. Guardar temporalmente y validar.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_layout_",
        suffix=".docx",
        dir=destino.parent
    )

    os.close(descriptor)
    temporal = Path(ruta_temporal)

    try:
        documento_word.save(str(temporal))

        validar_documento_word(temporal)

        # Publicar sin reemplazar archivos existentes.
        os.link(temporal, destino)

        return str(destino)

    finally:
        temporal.unlink(missing_ok=True)
