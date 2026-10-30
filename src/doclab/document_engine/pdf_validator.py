
from pathlib import Path
import pymupdf


class ErrorPDF(Exception):
    """Error general de validacion de PDF."""


class PDFProtegidoError(ErrorPDF):
    """El PDF requiere una contrasena."""


class PDFCorruptoError(ErrorPDF):
    """El PDF no puede procesarse correctamente."""


def validar_pdf(ruta_archivo):
    """
    Valida un archivo PDF antes de convertirlo.

    Comprueba:
    - Que el archivo exista.
    - Que tenga extension PDF.
    - Que pueda abrirse como PDF.
    - Que no requiera contrasena.
    - Que contenga al menos una pagina.
    - Que sus paginas puedan cargarse.

    Retorna:
        int: Numero de paginas del documento.

    Lanza:
        FileNotFoundError
        ValueError
        PDFProtegidoError
        PDFCorruptoError
    """

    ruta = Path(ruta_archivo)

    # 1. Comprobar que el archivo existe.
    if not ruta.is_file():
        raise FileNotFoundError(
            "El archivo PDF no existe."
        )

    # 2. Comprobar la extension.
    if ruta.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo debe tener extension PDF."
        )

    # 3. Intentar abrir el documento.
    try:
        documento = pymupdf.open(
            str(ruta),
            filetype="pdf"
        )

    except (
        pymupdf.FileDataError,
        pymupdf.EmptyFileError
    ) as error:
        raise PDFCorruptoError(
            "El archivo no contiene un PDF legible."
        ) from error

    # 4. Validar el contenido del documento.
    try:

        # Comprobar si requiere contrasena.
        if documento.needs_pass:
            raise PDFProtegidoError(
                "El documento esta protegido con contrasena."
            )

        # Comprobar que tenga paginas.
        numero_paginas = documento.page_count

        if numero_paginas == 0:
            raise PDFCorruptoError(
                "El documento no contiene paginas."
            )

        # Intentar cargar todas las paginas.
        for numero_pagina in range(numero_paginas):
            documento.load_page(numero_pagina)

        # Devolver el numero de paginas.
        return numero_paginas

    except pymupdf.FileDataError as error:
        raise PDFCorruptoError(
            "No fue posible leer las paginas del PDF."
        ) from error

    finally:
        # Cerrar siempre el documento.
        documento.close()
