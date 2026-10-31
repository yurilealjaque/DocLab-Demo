
"""
Motor OCR de DocLab.

Reconoce texto de paginas PDF mediante PyMuPDF.
Utiliza archivos de idioma almacenados localmente.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf


class RecursosOCRNoDisponiblesError(Exception):
    """Faltan archivos necesarios para ejecutar OCR."""


class ErrorReconocimientoOCR(Exception):
    """Ocurrio un error durante el reconocimiento."""


@dataclass(frozen=True)
class ResultadoOCR:
    numero_pagina: int
    texto: str
    idioma: str


def obtener_carpeta_tessdata():
    """
    Devuelve la ubicacion local de los modelos OCR.
    """

    carpeta_doclab = Path(__file__).resolve().parent.parent

    return carpeta_doclab / "resources" / "tessdata"


def verificar_recursos_ocr(
    carpeta_tessdata=None,
    idioma="spa+eng"
):
    """
    Verifica que existan los archivos de idioma.

    Devuelve la ruta de la carpeta tessdata.
    """

    if carpeta_tessdata is None:
        carpeta = obtener_carpeta_tessdata()
    else:
        carpeta = Path(carpeta_tessdata)

    idiomas = idioma.split("+")

    if not idiomas or any(
        not codigo.strip() for codigo in idiomas
    ):
        raise ValueError(
            "Debes indicar al menos un idioma valido."
        )

    if not carpeta.is_dir():
        raise RecursosOCRNoDisponiblesError(
            "No se encontro la carpeta de recursos OCR."
        )

    for codigo in idiomas:
        codigo = codigo.strip()

        archivo_idioma = carpeta / f"{codigo}.traineddata"

        if (
            not archivo_idioma.is_file()
            or archivo_idioma.stat().st_size == 0
        ):
            raise RecursosOCRNoDisponiblesError(
                f"No esta disponible el idioma OCR: {codigo}"
            )

    return carpeta


def reconocer_texto_pagina(
    ruta_archivo,
    numero_pagina,
    idioma="spa+eng",
    dpi=300,
    completo=False,
    carpeta_tessdata=None
):
    """
    Ejecuta OCR sobre una pagina PDF.

    numero_pagina comienza en 1.

    completo=False:
        Conserva el texto digital y reconoce
        zonas adicionales mediante OCR.

    completo=True:
        Realiza reconocimiento de toda la pagina.
    """

    if isinstance(numero_pagina, bool) or not isinstance(
        numero_pagina, int
    ) or numero_pagina < 1:
        raise ValueError(
            "El numero de pagina debe ser un entero positivo."
        )

    if isinstance(dpi, bool) or not isinstance(
        dpi, int
    ) or not 72 <= dpi <= 600:
        raise ValueError(
            "La resolucion OCR debe estar entre 72 y 600 DPI."
        )

    # 1. Validar el PDF mediante el modulo existente.
    total_paginas = validar_pdf(ruta_archivo)

    if numero_pagina > total_paginas:
        raise ValueError(
            "La pagina solicitada no existe en el documento."
        )

    # 2. Verificar los recursos locales.
    carpeta = verificar_recursos_ocr(
        carpeta_tessdata=carpeta_tessdata,
        idioma=idioma
    )

    # 3. Abrir y reconocer el contenido de la pagina.
    try:
        with pymupdf.open(
            str(ruta_archivo),
            filetype="pdf"
        ) as documento:

            pagina = documento.load_page(
                numero_pagina - 1
            )

            pagina_ocr = pagina.get_textpage_ocr(
                language=idioma,
                dpi=dpi,
                full=completo,
                tessdata=str(carpeta)
            )

            texto = pagina.get_text(
                "text",
                textpage=pagina_ocr
            )

    except Exception as error:
        raise ErrorReconocimientoOCR(
            "No fue posible reconocer el texto de la pagina."
        ) from error

    # 4. Entregar el resultado.
    return ResultadoOCR(
        numero_pagina=numero_pagina,
        texto=texto.strip(),
        idioma=idioma
    )
