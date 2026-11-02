
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImageReader

from doclab.document_engine.image_validator import validar_imagen
from doclab.document_engine.photo_manager import GestorFotografias


# Limite preventivo de dimensiones de pagina PDF.
LADO_MAXIMO_PUNTOS = 14000


class ErrorFotosPDF(Exception):
    """Error general al generar el PDF de fotografias."""


@dataclass(frozen=True)
class ResultadoFotosPDF:
    """Informacion del PDF generado."""

    ruta_destino: Path
    numero_paginas: int
    tamano_bytes: int


def _convertir_imagen_a_png(ruta_imagen: Path):
    """
    Lee una fotografia respetando su orientacion.

    Devuelve los bytes PNG y sus dimensiones reales.
    No modifica el archivo original.
    """

    lector = QImageReader(str(ruta_imagen))
    lector.setAutoTransform(True)

    imagen = lector.read()

    if imagen.isNull():
        raise ErrorFotosPDF(
            "No fue posible leer una de las fotografias."
        )

    ancho = imagen.width()
    alto = imagen.height()

    if ancho <= 0 or alto <= 0:
        raise ErrorFotosPDF(
            "Una fotografia tiene dimensiones invalidas."
        )

    # Prevenir dimensiones excesivas en el PDF.
    if max(ancho, alto) > LADO_MAXIMO_PUNTOS:
        raise ErrorFotosPDF(
            "Una fotografia supera las dimensiones "
            "permitidas para este generador PDF."
        )

    # Preparar imagen PNG en memoria.
    datos = QBuffer()

    if not datos.open(QIODevice.OpenModeFlag.WriteOnly):
        raise ErrorFotosPDF(
            "No fue posible preparar la fotografia."
        )

    try:
        if not imagen.save(datos, "PNG"):
            raise ErrorFotosPDF(
                "No fue posible preparar la imagen PNG."
            )

        contenido = bytes(datos.data())

    finally:
        datos.close()

    return contenido, ancho, alto


def generar_pdf_fotografias(
    gestor: GestorFotografias,
    ruta_destino,
) -> ResultadoFotosPDF:
    """
    Genera un PDF con una fotografia por pagina.

    Caracteristicas:
    - Conserva el orden del gestor.
    - Respeta la orientacion interpretada por Qt.
    - No modifica las fotografias originales.
    - No sobrescribe archivos existentes.
    - Utiliza un PDF temporal.
    - Comprueba cantidad de paginas e imagenes.
    - Limpia los temporales ante errores controlados.
    """

    # 1. Validar el gestor.
    if not isinstance(gestor, GestorFotografias):
        raise TypeError(
            "Se requiere un gestor de fotografias."
        )

    fotografias = gestor.obtener_fotografias()

    if not fotografias:
        raise ValueError(
            "Debes agregar al menos una fotografia."
        )

    # 2. Validar el destino.
    destino = Path(ruta_destino)

    if destino.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de destino debe ser PDF."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    if destino.exists():
        raise FileExistsError(
            "Ya existe un archivo con ese nombre."
        )

    # 3. Comprobar que el destino no sea un origen.
    destino_normalizado = os.path.normcase(
        str(destino.resolve())
    )

    for fotografia in fotografias:
        origen_normalizado = os.path.normcase(
            str(fotografia.ruta.resolve())
        )

        if origen_normalizado == destino_normalizado:
            raise ValueError(
                "El destino no puede ser una fotografia original."
            )

    # 4. Revalidar las fotografias.
    # Pueden haber cambiado despues de ser agregadas.
    for fotografia in fotografias:
        validar_imagen(fotografia.ruta)

    ruta_temporal = None

    # Crear documento PDF vacio.
    documento = pymupdf.open()

    try:
        # 5. Incorporar fotografias en el orden del gestor.
        for fotografia in fotografias:
            contenido, ancho, alto = _convertir_imagen_a_png(
                fotografia.ruta
            )

            pagina = documento.new_page(
                width=ancho,
                height=alto,
            )

            pagina.insert_image(
                pagina.rect,
                stream=contenido,
                keep_proportion=True,
            )

        # 6. Crear archivo temporal en carpeta destino.
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            prefix=".doclab_fotos_",
            dir=destino.parent,
            delete=False,
        ) as archivo_temporal:
            ruta_temporal = Path(archivo_temporal.name)

        # 7. Guardar el documento temporal.
        documento.save(
            str(ruta_temporal),
            garbage=3,
            deflate=True,
        )

        # IMPORTANTE:
        # No cerrar aqui el documento.
        # El bloque finally se encarga de ello.

        # 8. Comprobar el resultado.
        with pymupdf.open(str(ruta_temporal)) as comprobacion:

            if comprobacion.page_count != len(fotografias):
                raise ErrorFotosPDF(
                    "El PDF no contiene la cantidad "
                    "esperada de paginas."
                )

            for pagina in comprobacion:

                if pagina.rect.is_empty:
                    raise ErrorFotosPDF(
                        "El PDF contiene una pagina "
                        "sin dimensiones."
                    )

                if not pagina.get_images(full=True):
                    raise ErrorFotosPDF(
                        "El PDF contiene una pagina "
                        "sin imagen."
                    )

        # 9. Comprobar que no este vacio.
        if ruta_temporal.stat().st_size == 0:
            raise ErrorFotosPDF(
                "El PDF generado esta vacio."
            )

        # 10. Publicar sin sobrescribir.
        # os.link() falla si ya existe el destino.
        os.link(ruta_temporal, destino)

        # 11. Devolver informacion del resultado.
        return ResultadoFotosPDF(
            ruta_destino=destino,
            numero_paginas=len(fotografias),
            tamano_bytes=destino.stat().st_size,
        )

    finally:
        # 12. Cerrar el documento una sola vez.
        if not documento.is_closed:
            documento.close()

        # 13. Limpiar el archivo temporal.
        if ruta_temporal is not None:
            ruta_temporal.unlink(missing_ok=True)
