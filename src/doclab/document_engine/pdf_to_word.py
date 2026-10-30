
import os
import tempfile
import zipfile

from pathlib import Path
from pdf2docx import Converter


def validar_documento_word(ruta):
    """
    Comprueba que el archivo generado tenga
    una estructura DOCX basica.
    """

    if not zipfile.is_zipfile(ruta):
        raise ValueError(
            "El documento generado no es un DOCX valido."
        )

    with zipfile.ZipFile(ruta, "r") as documento:
        archivos = documento.namelist()

        elementos_necesarios = [
            "[Content_Types].xml",
            "word/document.xml",
        ]

        for elemento in elementos_necesarios:
            if elemento not in archivos:
                raise ValueError(
                    "El Word generado tiene una "
                    "estructura incompleta."
                )

        archivo_corrupto = documento.testzip()

        if archivo_corrupto is not None:
            raise ValueError(
                "El documento generado contiene "
                "datos ZIP corruptos."
            )


def convertir_pdf_a_word(ruta_origen, ruta_destino):
    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # 1. Validar las rutas.
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
            "El documento de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # 2. Crear archivo temporal.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_",
        suffix=".docx",
        dir=destino.parent
    )

    os.close(descriptor)

    temporal = Path(ruta_temporal)
    conversor = None

    try:
        # 3. Convertir el PDF.
        conversor = Converter(str(origen))
        conversor.convert(str(temporal))

        conversor.close()
        conversor = None

        # 4. Comprobar el resultado.
        if not temporal.is_file():
            raise RuntimeError(
                "No se genero el documento Word."
            )

        if temporal.stat().st_size == 0:
            raise RuntimeError(
                "El archivo Word generado esta vacio."
            )

        validar_documento_word(temporal)

        # 5. Publicar sin copiar ni sobrescribir.
        try:
            os.link(temporal, destino)

        except FileExistsError:
            raise FileExistsError(
                "Ya existe un documento en el destino."
            )

        except OSError as error:
            raise OSError(
                "No se pudo publicar el documento. "
                "Comprueba los permisos y que el sistema "
                "de archivos admita enlaces fisicos."
            ) from error

        return str(destino)

    finally:
        # 6. Cerrar el conversor si sigue abierto.
        if conversor is not None:
            conversor.close()

        # 7. Limpiar el nombre temporal.
        temporal.unlink(missing_ok=True)
