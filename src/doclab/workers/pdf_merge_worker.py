
"""
Trabajador para unir archivos PDF.

Ejecuta el servicio de union en un QThread
y comunica los resultados mediante senales.
"""

import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.pdf_merge_service import (
    ServicioUnionPDF
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError
)


logger = logging.getLogger("doclab.union_pdf")


class TrabajadorUnionPDF(QThread):
    """
    Ejecuta la union de archivos PDF
    sin bloquear el hilo principal de Qt.
    """

    union_exitosa = Signal(str)
    union_fallida = Signal(str)

    def __init__(self, rutas_origen, ruta_destino):
        super().__init__()

        self.rutas_origen = list(rutas_origen)
        self.ruta_destino = ruta_destino

    def run(self):
        """
        Ejecuta el servicio y emite una señal
        de exito o error.
        """

        logger.info("Inicio de union de archivos PDF")

        try:
            servicio = ServicioUnionPDF()

            resultado = servicio.unir(
                self.rutas_origen,
                self.ruta_destino
            )

            logger.info("Union PDF completada correctamente")

            self.union_exitosa.emit(resultado)

        except PDFProtegidoError:
            logger.warning(
                "Union rechazada: PDF protegido"
            )

            self.union_fallida.emit(
                "Uno de los archivos PDF esta protegido "
                "con contrasena y no puede procesarse."
            )

        except PDFCorruptoError:
            logger.warning(
                "Union rechazada: PDF corrupto"
            )

            self.union_fallida.emit(
                "Uno de los documentos PDF no es valido "
                "o contiene errores de lectura."
            )

        except FileExistsError:
            logger.warning(
                "Union rechazada: destino existente"
            )

            self.union_fallida.emit(
                "El archivo PDF de destino ya existe. "
                "Selecciona otro nombre."
            )

        except (FileNotFoundError, ValueError):
            logger.warning(
                "Union rechazada: archivos o rutas invalidas"
            )

            self.union_fallida.emit(
                "Comprueba que seleccionaste al menos "
                "dos archivos PDF validos y que la "
                "carpeta de destino existe."
            )

        except Exception:
            logger.exception(
                "Error inesperado durante la union PDF"
            )

            self.union_fallida.emit(
                "No fue posible unir los archivos PDF. "
                "Comprueba los documentos, el espacio "
                "disponible y los permisos de escritura."
            )
