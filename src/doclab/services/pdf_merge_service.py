
"""
Servicio de union de archivos PDF.

Coordina la operacion de union utilizando
el motor documental existente.
"""

from doclab.document_engine.pdf_merger import (
    unir_archivos_pdf
)


class ServicioUnionPDF:
    """
    Servicio encargado de coordinar
    la union de dos o mas archivos PDF.
    """

    def unir(self, rutas_origen, ruta_destino):
        """
        Solicita al motor la union de los PDF.

        Retorna:
            str: Ruta del documento generado.
        """

        resultado = unir_archivos_pdf(
            rutas_origen,
            ruta_destino
        )

        return resultado
