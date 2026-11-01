
"""
Trabajador para comprimir documentos PDF.

Responsabilidades:
- Ejecutar el servicio de compresión en QThread.
- Mantener receptiva la interfaz gráfica.
- Comunicar resultados mediante señales Qt.
- Diferenciar errores conocidos.
- Registrar eventos sin exponer rutas privadas.

No realiza operaciones de interfaz.
"""

import logging

from PySide6.QtCore import QThread, Signal

from doclab.services.pdf_compress_service import (
    ServicioCompresionPDF,
)

from doclab.document_engine.pdf_compressor import (
    SinReduccionError,
    DocumentoFirmadoError,
)

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError,
)


logger = logging.getLogger("doclab.compresion_pdf")


class TrabajadorCompresionPDF(QThread):
    """
    Ejecuta la compresión de un PDF en segundo plano.

    Señales:
        compresion_exitosa(object):
            Entrega un ResultadoCompresion.

        compresion_fallida(str):
            Entrega un mensaje comprensible.
    """

    compresion_exitosa = Signal(object)
    compresion_fallida = Signal(str)

    def __init__(
        self,
        ruta_origen,
        ruta_destino,
        parent=None
    ):
        super().__init__(parent)

        self.ruta_origen = ruta_origen
        self.ruta_destino = ruta_destino

    def run(self):
        """
        Ejecuta el servicio de compresión.

        Al llamar start(), Qt ejecuta este método
        en un hilo secundario.
        """

        logger.info("Inicio de compresion PDF")

        try:
            servicio = ServicioCompresionPDF()

            resultado = servicio.comprimir(
                self.ruta_origen,
                self.ruta_destino
            )

            logger.info(
                "Compresion PDF completada correctamente"
            )

            self.compresion_exitosa.emit(resultado)

        except SinReduccionError:
            logger.info(
                "El documento no obtuvo reduccion de tamano"
            )

            self.compresion_fallida.emit(
                "No se obtuvo una reducción del tamaño. "
                "El documento original permanece intacto."
            )

        except DocumentoFirmadoError:
            logger.warning(
                "Compresion rechazada: posible firma digital"
            )

            self.compresion_fallida.emit(
                "El documento contiene una posible firma "
                "digital o no pudo inspeccionarse por completo. "
                "Por seguridad, no se realizó la compresión."
            )

        except PDFProtegidoError:
            logger.warning(
                "Compresion rechazada: PDF protegido"
            )

            self.compresion_fallida.emit(
                "El documento PDF está protegido "
                "con contraseña y no puede comprimirse."
            )

        except PDFCorruptoError:
            logger.warning(
                "Compresion rechazada: PDF corrupto"
            )

            self.compresion_fallida.emit(
                "El documento PDF no es válido "
                "o presenta problemas de lectura."
            )

        except FileExistsError:
            logger.warning(
                "Compresion rechazada: destino existente"
            )

            self.compresion_fallida.emit(
                "Ya existe un archivo en la ubicación "
                "seleccionada. Elige otro nombre."
            )

        except (FileNotFoundError, ValueError):
            logger.warning(
                "Compresion rechazada: ruta o archivo invalido"
            )

            self.compresion_fallida.emit(
                "Comprueba que el documento existe, "
                "que es un PDF válido y que la carpeta "
                "de destino está disponible."
            )

        except Exception:
            logger.exception(
                "Error inesperado durante la compresion PDF"
            )

            self.compresion_fallida.emit(
                "No fue posible comprimir el documento. "
                "Comprueba los permisos, el espacio disponible "
                "y el estado del archivo original."
            )
