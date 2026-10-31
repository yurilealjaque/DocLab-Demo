
"""
Trabajador de conversion PDF a Word con OCR.

Ejecuta el servicio OCR en un hilo separado
para no bloquear la interfaz grafica.
"""

import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.ocr_conversion_service import (
    ServicioConversionOCR
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError
)

from doclab.document_engine.ocr_engine import (
    RecursosOCRNoDisponiblesError,
    ErrorReconocimientoOCR
)


logger = logging.getLogger("doclab.conversion")


class TrabajadorConversionOCR(QThread):

    conversion_exitosa = Signal(str)
    conversion_fallida = Signal(str)

    def __init__(self, origen, destino):
        super().__init__()

        self.origen = origen
        self.destino = destino

    def run(self):
        """
        Ejecuta la conversion OCR completa.
        """

        logger.info(
            "Inicio de conversion PDF a Word con OCR"
        )

        try:
            servicio = ServicioConversionOCR()

            resultado = servicio.convertir(
                origen=self.origen,
                destino=self.destino
            )

            logger.info(
                "Conversion OCR completada: %s paginas, "
                "%s con OCR, %s imagenes",
                resultado.total_paginas,
                resultado.paginas_con_ocr,
                resultado.imagenes_exportadas
            )

            self.conversion_exitosa.emit(
                resultado.ruta_destino
            )

        except PDFProtegidoError:

            logger.warning(
                "Conversion OCR rechazada: PDF protegido"
            )

            self.conversion_fallida.emit(
                "El PDF esta protegido con contrasena. "
                "DocLab no puede procesarlo."
            )

        except PDFCorruptoError:

            logger.warning(
                "Conversion OCR rechazada: PDF corrupto"
            )

            self.conversion_fallida.emit(
                "El documento PDF no es valido "
                "o contiene errores de lectura."
            )

        except RecursosOCRNoDisponiblesError:

            logger.warning(
                "Recursos OCR no disponibles"
            )

            self.conversion_fallida.emit(
                "No se encontraron los modelos de idioma "
                "necesarios para realizar el OCR. "
                "Verifica la carpeta resources/tessdata."
            )

        except ErrorReconocimientoOCR:

            logger.exception(
                "Fallo el reconocimiento OCR"
            )

            self.conversion_fallida.emit(
                "Ocurrio un error durante el reconocimiento "
                "de texto. Revisa el PDF e intenta nuevamente."
            )

        except FileExistsError:

            logger.warning(
                "El archivo de destino ya existe"
            )

            self.conversion_fallida.emit(
                "El documento Word de destino ya existe. "
                "Selecciona otro nombre."
            )

        except Exception:

            logger.exception(
                "Error inesperado en conversion OCR"
            )

            self.conversion_fallida.emit(
                "No fue posible completar la conversion "
                "con OCR. Comprueba el documento, "
                "el espacio disponible y los permisos "
                "de escritura."
            )
