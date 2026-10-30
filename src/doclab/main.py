
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from doclab.ui.main_window import VentanaPrincipal
from doclab.infrastructure.logger import configurar_logging


def main():
    # Inicializar el sistema de registros
    configurar_logging()

    aplicacion = QApplication(sys.argv)

    ruta_estilos = (
        Path(__file__).parent
        / "ui"
        / "styles"
        / "theme.qss"
    )

    if ruta_estilos.exists():
        estilos = ruta_estilos.read_text(
            encoding="utf-8"
        )
        aplicacion.setStyleSheet(estilos)

    ventana = VentanaPrincipal()
    ventana.show()

    return aplicacion.exec()


if __name__ == "__main__":
    sys.exit(main())

