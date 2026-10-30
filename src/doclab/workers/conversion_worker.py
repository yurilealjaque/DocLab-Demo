
import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.conversion_service import (ServicioConversion)

from doclab.document_engine.pdf_validator import ( PDFProtegidoError, PDFCorruptoError,)
from doclab.document_engine.pdf_content_detector import (ResultadoInspeccionPDF)

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

        
        except PDFProtegidoError:
            logger.warning("PDF protegido con contrasena")

            self.conversion_fallida.emit(
                "El PDF esta protegido con contrasena. "
                "Esta version de DocLab no puede convertirlo."
            )

        except PDFCorruptoError:
            logger.warning("PDF invalido o corrupto")

            self.conversion_fallida.emit(
                "El documento PDF no es valido o "
                "contiene errores que impiden leerlo."
            )

        except Exception as error:
            logger.error(
                "Fallo de conversion: %s",
                type(error).__name__
            )

            self.conversion_fallida.emit(
                "No fue posible convertir el documento. "
                "Comprueba el archivo y los permisos "
                "de escritura."
            )



class TrabajadorInspeccion(QThread):
    """
    Inspecciona el contenido de un PDF
    sin bloquear la interfaz grafica.
    """

    inspeccion_exitosa = Signal(object)
    inspeccion_fallida = Signal(str)

    def __init__(self, origen):
        super().__init__()

        self.origen = origen

    def run(self):
        """
        Ejecuta el servicio de inspeccion
        en un hilo independiente.
        """

        logger.info("Inicio de inspeccion PDF")

        try:
            servicio = ServicioConversion()

            resultado = servicio.inspeccionar(
                self.origen
            )

            logger.info(
                "Inspeccion PDF finalizada: %s",
                resultado.clasificacion
            )

            self.inspeccion_exitosa.emit(resultado)

        except PDFProtegidoError:
            logger.warning(
                "Inspeccion rechazada: PDF protegido"
            )

            self.inspeccion_fallida.emit(
                "El documento PDF esta protegido "
                "con contrasena."
            )

        except PDFCorruptoError:
            logger.warning(
                "Inspeccion rechazada: PDF corrupto"
            )

            self.inspeccion_fallida.emit(
                "El documento PDF no es valido "
                "o contiene errores de lectura."
            )

        except Exception as error:
            logger.error(
                "Fallo de inspeccion: %s",
                type(error).__name__
            )

            self.inspeccion_fallida.emit(
                "No fue posible analizar el "
                "contenido del documento PDF."
            )
