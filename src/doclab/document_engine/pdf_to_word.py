
from pathlib import Path
from pdf2docx import Converter


def convertir_pdf_a_word(ruta_origen, ruta_destino):
    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # Comprobar que el documento existe.
    if not origen.is_file():
        raise FileNotFoundError(
            "El archivo PDF no existe."
        )

    # Comprobar el formato de entrada.
    if origen.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de origen debe ser un PDF."
        )

    # Comprobar el formato de salida.
    if destino.suffix.lower() != ".docx":
        raise ValueError(
            "El archivo de destino debe ser DOCX."
        )

    # Evitar sobrescribir un documento existente.
    if destino.exists():
        raise FileExistsError(
            "Ya existe un archivo en la ruta de destino."
        )

    conversor = None

    try:
        conversor = Converter(str(origen))
        conversor.convert(str(destino))

        # Comprobar que se genero un archivo.
        if not destino.is_file():
            raise RuntimeError(
                "No se genero el documento Word."
            )

        if destino.stat().st_size == 0:
            raise RuntimeError(
                "El documento generado esta vacio."
            )

        return str(destino)

    finally:
        if conversor is not None:
            conversor.close()
