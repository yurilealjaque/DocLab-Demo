
import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.conversion_service import (
    ServicioConversion
)


logger = logging.getLogger("doclab.conversion")


class TrabajadorConversion(QThread):

    conversion_exitosa = Signal(str)
    conversion_fallida = Signal(str)

    def __init__(self, origen, destino):
        super().__init__()

        self.origen = origen
        self.destino = destino

    def run(self):
        logger.info("Inicio de conversion PDF a Word")

        try:
            servicio = ServicioConversion()

            resultado = servicio.convertir(
                self.origen,
                self.destino
            )

            logger.info("Conversion finalizada correctamente")
            self.conversion_exitosa.emit(resultado)

        except Exception as error:
            logger.error(
                "Error durante la conversion: %s",
                type(error).__name__
            )

            self.conversion_fallida.emit(
                f"No fue posible convertir el documento. "
                f"Error: {type(error).__name__}"
            )
