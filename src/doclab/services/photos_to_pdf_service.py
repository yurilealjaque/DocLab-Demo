
"""
Servicio de generación de PDF a partir de fotografías.

Responsabilidades:
- Recibir el gestor de fotografías.
- Solicitar la generación del documento.
- Devolver el resultado del motor.
- Propagar los errores sin ocultarlos.

No depende de componentes gráficos de PySide6.
"""

from doclab.document_engine.photo_manager import GestorFotografias

from doclab.document_engine.photos_to_pdf import (
    generar_pdf_fotografias,
    ResultadoFotosPDF,
)


class ServicioFotosPDF:
    """
    Coordina la generación de documentos PDF
    a partir de fotografías previamente organizadas.
    """

    def generar(
        self,
        gestor: GestorFotografias,
        ruta_destino,
    ) -> ResultadoFotosPDF:
        """
        Solicita al motor la generación del PDF.

        Parámetros:
            gestor: colección ordenada de fotografías.
            ruta_destino: ubicación del PDF resultante.

        Retorna:
            ResultadoFotosPDF con la ruta, cantidad
            de páginas y tamaño del documento.

        Las excepciones se propagan a la capa superior.
        """

        resultado = generar_pdf_fotografias(
            gestor,
            ruta_destino,
        )

        return resultado
