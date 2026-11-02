"""Ajustes no destructivos de brillo y contraste para imágenes Qt.

Este módulo solo transforma QImage en memoria. No escribe archivos.
Los parámetros son enteros de -100 a 100; cero significa sin ajuste.
"""

import numpy as np
from PySide6.QtGui import QImage


class ErrorAjusteImagen(ValueError):
    """Los parámetros o la imagen no permiten realizar el ajuste."""


def _validar_ajuste(nombre: str, valor: int) -> None:
    if type(valor) is not int or not -100 <= valor <= 100:
        raise ErrorAjusteImagen(
            f"El {nombre} debe ser un número entero entre -100 y 100."
        )


def ajustar_brillo_contraste(
    imagen: QImage,
    brillo: int = 0,
    contraste: int = 0,
) -> QImage:
    """Retorna una nueva imagen ajustada, sin modificar la original.

    brillo: -100 deja RGB negro y +100 desplaza RGB hacia blanco.
    contraste: -100 uniforma los canales a gris medio y +100 duplica
              su desviación respecto de 127,5.
    Conserva el canal alfa y las dimensiones de la imagen.
    """
    _validar_ajuste("brillo", brillo)
    _validar_ajuste("contraste", contraste)

    if not isinstance(imagen, QImage) or imagen.isNull():
        raise ErrorAjusteImagen("Se requiere una imagen válida.")

    # La copia garantiza que nunca se modifica la imagen recibida.
    resultado = imagen.convertToFormat(QImage.Format.Format_RGBA8888)
    if brillo == 0 and contraste == 0:
        return resultado

    ancho = resultado.width()
    alto = resultado.height()
    paso = resultado.bytesPerLine()

    # Conservar una copia escribible de los píxeles. El padding de cada fila
    # queda intacto y QImage recibe su propia copia al terminar.
    datos = np.frombuffer(bytes(resultado.constBits()), dtype=np.uint8).copy()
    filas = datos.reshape((alto, paso))
    pixeles = filas[:, : ancho * 4].reshape((alto, ancho, 4))

    rgb = pixeles[:, :, :3].astype(np.float32)
    factor = 1.0 + contraste / 100.0
    desplazamiento = brillo * 255.0 / 100.0
    rgb = (rgb - 127.5) * factor + 127.5 + desplazamiento
    pixeles[:, :, :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)

    # copy() independiza al QImage final del buffer temporal de NumPy.
    return QImage(
        datos.data,
        ancho,
        alto,
        paso,
        QImage.Format.Format_RGBA8888,
    ).copy()
