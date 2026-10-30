
"""
Calcula la cobertura de imagenes en una pagina PDF.

No ejecuta OCR ni confirma que una pagina
sea un documento escaneado.
"""

import pymupdf


def calcular_cobertura_imagen(pagina):
    """
    Calcula la mayor proporcion de superficie
    ocupada por una imagen visible.

    Retorna un numero entre 0.0 y 1.0.

    Ejemplo:
        0.90 significa que una imagen cubre
        el 90 % de la superficie de la pagina.
    """

    rectangulo_pagina = pagina.rect

    area_pagina = rectangulo_pagina.get_area()

    if area_pagina <= 0:
        return 0.0

    mayor_cobertura = 0.0

    imagenes = pagina.get_image_info()

    for imagen in imagenes:

        # Obtener las coordenadas de la imagen.
        rectangulo_imagen = pymupdf.Rect(
            imagen["bbox"]
        )

        # Considerar solo la porcion que cae
        # dentro de los limites de la pagina.
        area_visible = (
            rectangulo_imagen & rectangulo_pagina
        ).get_area()

        cobertura = area_visible / area_pagina

        if cobertura > mayor_cobertura:
            mayor_cobertura = cobertura

    return min(mayor_cobertura, 1.0)


def es_posible_escaneo(pagina, umbral=0.80):
    """
    Comprueba si una imagen individual ocupa
    al menos el porcentaje indicado.

    No analiza todavia si existe texto digital.
    """

    if not 0 < umbral <= 1:
        raise ValueError(
            "El umbral debe estar entre 0 y 1."
        )

    cobertura = calcular_cobertura_imagen(pagina)

    return cobertura >= umbral
