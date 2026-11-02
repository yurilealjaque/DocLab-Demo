
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from doclab.ui.main_window import VentanaPrincipal
from doclab.infrastructure.logger import configurar_logging


def obtener_ruta_recurso(*partes):
    """
    Obtiene la ruta de un recurso de DocLab.

    Compatible con:
    - Ejecución desde el código fuente.
    - Ejecutable generado mediante PyInstaller.
    """

    if getattr(sys, "frozen", False):
        carpeta_base = Path(sys._MEIPASS) / "doclab"
    else:
        carpeta_base = Path(__file__).resolve().parent

    return carpeta_base.joinpath(*partes)


def main():
    # Inicializar el sistema de registros
    configurar_logging()

    aplicacion = QApplication(sys.argv)

    # ---------------------------------------
    # ICONO DE DOCLAB
    # ---------------------------------------

    ruta_icono = obtener_ruta_recurso(
    "resources",
    "icons",
    "doclab.ico"
    )
    if ruta_icono.is_file():
        aplicacion.setWindowIcon(
            QIcon(str(ruta_icono))
        )

    # ---------------------------------------
    # ESTILOS DE LA APLICACIÓN
    # ---------------------------------------

    ruta_estilos = obtener_ruta_recurso(
    "ui",
    "styles",
    "theme.qss"
    )

    if ruta_estilos.exists():
        estilos = ruta_estilos.read_text(
            encoding="utf-8"
        )
        aplicacion.setStyleSheet(estilos)

    # ---------------------------------------
    # VENTANA PRINCIPAL
    # ---------------------------------------

    ventana = VentanaPrincipal()
    ventana.show()

    return aplicacion.exec()


if __name__ == "__main__":
    sys.exit(main())
