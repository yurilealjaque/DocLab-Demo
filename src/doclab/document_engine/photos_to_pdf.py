"""Generación segura de documentos PDF a partir de imágenes ordenadas.

La orientación EXIF se aplica al leer cada imagen. Después se incorpora
la rotación manual indicada en GestorFotografias, sin tocar los originales.
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImageReader, QTransform

from doclab.document_engine.image_validator import validar_imagen
from doclab.document_engine.photo_manager import GestorFotografias


LADO_MAXIMO_PUNTOS = 14000


class ErrorFotosPDF(Exception):
    """Error general al generar el PDF de imágenes."""


@dataclass(frozen=True)
class ResultadoFotosPDF:
    """Información del archivo generado."""

    ruta_destino: Path
    numero_paginas: int
    tamano_bytes: int


def _convertir_imagen_a_png(ruta_imagen: Path, rotacion: int = 0):
    """Devuelve bytes PNG y dimensiones tras EXIF y rotación manual.

    El argumento rotacion son grados horarios (0, 90, 180 o 270).
    La imagen original nunca se modifica.
    """
    if type(rotacion) is not int or rotacion not in (0, 90, 180, 270):
        raise ValueError("La rotación debe ser 0, 90, 180 o 270 grados.")

    lector = QImageReader(str(ruta_imagen))
    lector.setAutoTransform(True)
    imagen = lector.read()

    if imagen.isNull():
        raise ErrorFotosPDF("No fue posible leer una de las imágenes.")

    # Qt emplea un sistema de coordenadas visual con eje Y hacia abajo;
    # 90 grados positivos producen un giro horario de la imagen.
    if rotacion:
        imagen = imagen.transformed(QTransform().rotate(rotacion))

    ancho = imagen.width()
    alto = imagen.height()

    if ancho <= 0 or alto <= 0:
        raise ErrorFotosPDF("Una imagen tiene dimensiones inválidas.")

    if max(ancho, alto) > LADO_MAXIMO_PUNTOS:
        raise ErrorFotosPDF(
            "Una imagen supera las dimensiones permitidas "
            "para este generador PDF."
        )

    datos = QBuffer()
    if not datos.open(QIODevice.OpenModeFlag.WriteOnly):
        raise ErrorFotosPDF("No fue posible preparar la imagen.")

    try:
        if not imagen.save(datos, "PNG"):
            raise ErrorFotosPDF("No fue posible preparar la imagen PNG.")
        contenido = bytes(datos.data())
    finally:
        datos.close()

    return contenido, ancho, alto


def generar_pdf_fotografias(
    gestor: GestorFotografias,
    ruta_destino,
) -> ResultadoFotosPDF:
    """Genera un PDF multipágina con orden y rotaciones del gestor.

    Valida cada archivo, no sobrescribe destinos existentes, publica
    mediante archivo temporal y conserva intactas las imágenes originales.
    """
    if not isinstance(gestor, GestorFotografias):
        raise TypeError("Se requiere un gestor de fotografías.")

    fotografias = gestor.obtener_fotografias()
    if not fotografias:
        raise ValueError("Debes agregar al menos una imagen.")

    destino = Path(ruta_destino)
    if destino.suffix.lower() != ".pdf":
        raise ValueError("El archivo de destino debe ser PDF.")
    if not destino.parent.is_dir():
        raise FileNotFoundError("La carpeta de destino no existe.")
    if destino.exists() or destino.is_symlink():
        raise FileExistsError("Ya existe un archivo con ese nombre.")

    destino_normalizado = os.path.normcase(str(destino.resolve()))
    for fotografia in fotografias:
        origen_normalizado = os.path.normcase(str(fotografia.ruta.resolve()))
        if origen_normalizado == destino_normalizado:
            raise ValueError("El destino no puede ser una imagen original.")

    for fotografia in fotografias:
        validar_imagen(fotografia.ruta)

    # Congelar las rotaciones antes de construir el PDF. El trabajador
    # ya impide editar el gestor desde la interfaz durante la operación.
    rotaciones = tuple(
        gestor.obtener_rotacion(indice)
        for indice in range(len(fotografias))
    )

    ruta_temporal = None
    documento = pymupdf.open()

    try:
        for fotografia, rotacion in zip(fotografias, rotaciones):
            contenido, ancho, alto = _convertir_imagen_a_png(
                fotografia.ruta,
                rotacion,
            )
            pagina = documento.new_page(width=ancho, height=alto)
            pagina.insert_image(
                pagina.rect,
                stream=contenido,
                keep_proportion=True,
            )

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            prefix=".doclab_fotos_",
            dir=destino.parent,
            delete=False,
        ) as archivo_temporal:
            ruta_temporal = Path(archivo_temporal.name)

        documento.save(
            str(ruta_temporal),
            garbage=3,
            deflate=True,
        )

        with pymupdf.open(str(ruta_temporal)) as comprobacion:
            if comprobacion.page_count != len(fotografias):
                raise ErrorFotosPDF(
                    "El PDF no contiene la cantidad esperada de páginas."
                )
            for pagina in comprobacion:
                if pagina.rect.is_empty:
                    raise ErrorFotosPDF(
                        "El PDF contiene una página sin dimensiones."
                    )
                if not pagina.get_images(full=True):
                    raise ErrorFotosPDF(
                        "El PDF contiene una página sin imagen."
                    )

        if ruta_temporal.stat().st_size == 0:
            raise ErrorFotosPDF("El PDF generado está vacío.")

        # Publica solo si el destino todavía no existe.
        os.link(ruta_temporal, destino)

        return ResultadoFotosPDF(
            ruta_destino=destino,
            numero_paginas=len(fotografias),
            tamano_bytes=destino.stat().st_size,
        )
    finally:
        if not documento.is_closed:
            documento.close()
        if ruta_temporal is not None:
            ruta_temporal.unlink(missing_ok=True)
