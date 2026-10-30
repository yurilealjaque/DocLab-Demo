
import os
import tempfile
from pathlib import Path

from pdf2docx import Converter


def convertir_pdf_a_word(ruta_origen, ruta_destino):
    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # Validar el documento de entrada.
    if not origen.is_file():
        raise FileNotFoundError(
            "El archivo PDF no existe."
        )

    if origen.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de origen debe ser PDF."
        )

    if destino.suffix.lower() != ".docx":
        raise ValueError(
            "El archivo de destino debe ser DOCX."
        )

    if destino.exists():
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # Crear un archivo temporal en la carpeta
    # donde se guardara el Word definitivo.
    descriptor, ruta_temporal = tempfile.mkstemp(
        suffix=".docx",
        prefix="doclab_",
        dir=destino.parent
    )

    os.close(descriptor)

    temporal = Path(ruta_temporal)
    conversor = None

    try:
        conversor = Converter(str(origen))

        conversor.convert(str(temporal))

        # Cerrar antes de publicar el resultado.
        conversor.close()
        conversor = None

        if not temporal.is_file():
            raise RuntimeError(
                "No se genero el archivo Word."
            )

        if temporal.stat().st_size == 0:
            raise RuntimeError(
                "El archivo Word generado esta vacio."
            )

         # Publicar el documento sin sobrescribir.
        # Solo eliminaremos el destino si esta
        # operacion fue quien lo creo.
        destino_creado = False

        try:
            with temporal.open("rb") as archivo_origen:
                with destino.open("xb") as archivo_destino:
                    destino_creado = True

                    while True:
                        bloque = archivo_origen.read(
                            1024 * 1024
                        )

                        if not bloque:
                            break

                        archivo_destino.write(bloque)

            return str(destino)

        except Exception:
            if destino_creado:
                destino.unlink(missing_ok=True)

            raise

    finally:
        if conversor is not None:
            conversor.close()

        temporal.unlink(missing_ok=True)