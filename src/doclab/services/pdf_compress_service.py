
"""
Servicio de compresión de documentos PDF.

Responsabilidades:
- Recibir una solicitud de compresión.
- Delegar el procesamiento al motor documental.
- Retornar la información del resultado.
- Propagar las excepciones para su tratamiento
  en las capas superiores.

No depende de PySide6.
"""

from doclab.document_engine.pdf_compressor import (
    comprimir_pdf,
    ResultadoCompresion,
)


class ServicioCompresionPDF:
    """
    Coordina la compresión de documentos PDF
    mediante el motor documental de DocLab.
    """

    def comprimir(self, ruta_origen, ruta_destino):
        """
        Solicita la compresión sin pérdida intencional.

        Parámetros:
            ruta_origen: PDF que se desea optimizar.
            ruta_destino: ubicación del PDF resultante.

        Retorna:
            ResultadoCompresion con información
            del tamaño original, tamaño final,
            cantidad de páginas y ahorro.

        Las excepciones del motor se propagan
        sin modificación.
        """

        resultado = comprimir_pdf(
            ruta_origen,
            ruta_destino
        )

        return resultado
