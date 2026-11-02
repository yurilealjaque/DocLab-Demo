
"""
Trabajador para generar documentos PDF desde fotografias.

Ejecuta el servicio fuera del hilo principal de Qt
y comunica el resultado mediante señales.

No modifica directamente la interfaz grafica.
"""

import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.photos_to_pdf_service import (
    ServicioFotosPDF,
)

from doclab.document_engine.image_validator import (
    ImagenCorruptaError,
    ImagenDemasiadoGrandeError,
)

from doclab.document_engine.photos_to_pdf import (
    ErrorFotosPDF,
)


logger = logging.getLogger("doclab.fotografias_pdf")


class TrabajadorFotosPDF(QThread):
    """
    Genera un PDF utilizando las fotografias del gestor.

    Señales:
        generacion_exitosa(object):
            Entrega un ResultadoFotosPDF.

        generacion_fallida(str):
            Entrega un mensaje comprensible.
    """

    generacion_exitosa = Signal(object)
    generacion_fallida = Signal(str)

    def __init__(
        self,
        gestor,
        ruta_destino,
        parent=None,
    ):
        super().__init__(parent)

        self.gestor = gestor
        self.ruta_destino = ruta_destino

    def run(self):
        """Ejecuta la generacion del PDF."""

        logger.info(
            "Inicio de generacion PDF desde fotografias"
        )

        try:
            servicio = ServicioFotosPDF()

            resultado = servicio.generar(
                self.gestor,
                self.ruta_destino,
            )

            logger.info(
                "Generacion PDF desde fotografias completada"
            )

            self.generacion_exitosa.emit(resultado)

        except ImagenDemasiadoGrandeError:
            logger.warning(
                "Generacion rechazada: imagen demasiado grande"
            )

            self.generacion_fallida.emit(
                "Una de las fotografías supera los límites "
                "de tamaño o resolución permitidos."
            )

        except ImagenCorruptaError:
            logger.warning(
                "Generacion rechazada: imagen corrupta"
            )

            self.generacion_fallida.emit(
                "Una de las fotografías está dañada "
                "o no contiene una imagen válida."
            )

        except FileExistsError:
            logger.warning(
                "Generacion rechazada: destino existente"
            )

            self.generacion_fallida.emit(
                "Ya existe un archivo PDF con ese nombre. "
                "Selecciona otro destino."
            )

        except FileNotFoundError:
            logger.warning(
                "Generacion rechazada: archivo inexistente"
            )

            self.generacion_fallida.emit(
                "No se encontró una de las fotografías "
                "o la carpeta de destino no existe."
            )

        except ValueError:
            logger.warning(
                "Generacion rechazada: solicitud invalida"
            )

            self.generacion_fallida.emit(
                "Comprueba que seleccionaste fotografías "
                "válidas y un destino con extensión PDF."
            )

        except ErrorFotosPDF:
            logger.warning(
                "Error controlado durante generacion PDF"
            )

            self.generacion_fallida.emit(
                "No fue posible preparar o generar el PDF "
                "con las fotografías seleccionadas."
            )

        except OSError:
            logger.exception(
                "Error de archivos durante generacion PDF"
            )

            self.generacion_fallida.emit(
                "No fue posible guardar el PDF. Comprueba "
                "los permisos y el espacio disponible."
            )

        except Exception:
            logger.exception(
                "Error inesperado durante generacion PDF"
            )

            self.generacion_fallida.emit(
                "Ocurrió un error inesperado al generar "
                "el documento PDF."
            )
