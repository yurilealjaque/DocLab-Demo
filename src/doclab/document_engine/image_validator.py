
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QImageReader


# Limites preventivos para la primera version.
TAMANO_MAXIMO_MB = 25
PIXELES_MAXIMOS = 20_000_000

FORMATOS_PERMITIDOS = {
    ".jpg": b"jpeg",
    ".jpeg": b"jpeg",
    ".png": b"png",
}


class ErrorImagen(Exception):
    """Error general durante la validacion de imagenes."""


class ImagenCorruptaError(ErrorImagen):
    """La imagen no tiene un contenido legible o valido."""


class ImagenDemasiadoGrandeError(ErrorImagen):
    """La imagen supera los limites permitidos."""


@dataclass(frozen=True)
class InformacionImagen:
    """Informacion obtenida al validar una fotografia."""

    ruta: Path
    formato: str
    ancho: int
    alto: int
    tamano_bytes: int
    requiere_rotacion: bool


def validar_imagen(ruta_archivo) -> InformacionImagen:
    """
    Valida una fotografia JPG, JPEG o PNG.

    No modifica el archivo original.

    Comprueba existencia, extension, formato real,
    tamano, dimensiones y lectura del contenido.
    """

    ruta = Path(ruta_archivo)

    # 1. Comprobar que exista un archivo.
    if not ruta.is_file():
        raise FileNotFoundError(
            "El archivo de imagen no existe."
        )

    # 2. Comprobar la extension.
    extension = ruta.suffix.lower()

    if extension not in FORMATOS_PERMITIDOS:
        raise ValueError(
            "Solo se permiten imagenes JPG, JPEG y PNG."
        )

    # 3. Comprobar el tamano del archivo.
    tamano_bytes = ruta.stat().st_size

    if tamano_bytes == 0:
        raise ImagenCorruptaError(
            "El archivo de imagen esta vacio."
        )

    limite_bytes = TAMANO_MAXIMO_MB * 1024 * 1024

    if tamano_bytes > limite_bytes:
        raise ImagenDemasiadoGrandeError(
            "La imagen supera el limite de "
            f"{TAMANO_MAXIMO_MB} MB."
        )

    # 4. Comprobar la firma del archivo.
    try:
        with ruta.open("rb") as archivo:
            cabecera = archivo.read(8)
    except OSError as error:
        raise ErrorImagen(
            "No fue posible leer la imagen."
        ) from error

    if extension in (".jpg", ".jpeg"):
        firma_valida = cabecera.startswith(b"\xff\xd8\xff")
    else:
        firma_valida = cabecera == b"\x89PNG\r\n\x1a\n"

    if not firma_valida:
        raise ImagenCorruptaError(
            "El contenido no coincide con el formato de imagen."
        )

    # 5. Abrir con el lector de Qt.
    lector = QImageReader(str(ruta))
    lector.setAutoTransform(True)

    formato_real = bytes(lector.format()).lower()

    if formato_real != FORMATOS_PERMITIDOS[extension]:
        raise ImagenCorruptaError(
            "El formato real de la imagen no coincide "
            "con su extension."
        )

    # 6. Consultar las dimensiones antes de decodificar.
    dimensiones = lector.size()

    if not dimensiones.isValid():
        raise ImagenCorruptaError(
            "No fue posible obtener las dimensiones."
        )

    ancho = dimensiones.width()
    alto = dimensiones.height()

    if ancho <= 0 or alto <= 0:
        raise ImagenCorruptaError(
            "La imagen tiene dimensiones invalidas."
        )

    if ancho * alto > PIXELES_MAXIMOS:
        raise ImagenDemasiadoGrandeError(
            "La resolucion de la imagen supera "
            "el limite permitido."
        )

    # 7. Consultar si Qt detecta una transformacion.
    # Puede incluir orientacion EXIF en fotografias JPEG.
    requiere_rotacion = lector.transformation().value != 0

    # 8. Intentar decodificar el contenido completo.
    imagen = lector.read()

    if imagen.isNull():
        raise ImagenCorruptaError(
            "No fue posible decodificar la imagen."
        )

    # 9. Devolver los metadatos.
    return InformacionImagen(
        ruta=ruta,
        formato=formato_real.decode("ascii"),
        ancho=ancho,
        alto=alto,
        tamano_bytes=tamano_bytes,
        requiere_rotacion=requiere_rotacion,
    )
