
from doclab.document_engine.pdf_validator import (
    validar_pdf
)

from doclab.document_engine.pdf_to_word import (
    convertir_pdf_a_word
)

from doclab.document_engine.pdf_content_detector import (
    inspeccionar_contenido_pdf
)


class ServicioConversion:

    def inspeccionar(self, origen):
        """
        Analiza el contenido de un PDF.

        Retorna un ResultadoInspeccionPDF
        con su clasificacion y las paginas
        con y sin texto extraible.
        """

        resultado = inspeccionar_contenido_pdf(origen)

        return resultado

    def convertir(self, origen, destino):
        """
        Valida y convierte un PDF a Word.
        """

        # Primero validar el documento.
        validar_pdf(origen)

        # Si es valido, convertir a Word.
        resultado = convertir_pdf_a_word(
            origen,
            destino
        )

        return resultado
