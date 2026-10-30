
from PySide6.QtCore import QThread, Signal

from doclab.services.conversion_service import (
    ServicioConversion
)


class TrabajadorConversion(QThread):

    conversion_exitosa = Signal(str)
    conversion_fallida = Signal(str)

    def __init__(self, origen, destino):
        super().__init__()

        self.origen = origen
        self.destino = destino

    def run(self):
        try:
            servicio = ServicioConversion()

            resultado = servicio.convertir(
                self.origen,
                self.destino
            )

            self.conversion_exitosa.emit(resultado)

        except Exception as error:
            self.conversion_fallida.emit(str(error))
