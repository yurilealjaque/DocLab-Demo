
from doclab.document_engine.pdf_to_word import (
    convertir_pdf_a_word
)


class ServicioConversion:

    def convertir(self, origen, destino):
        resultado = convertir_pdf_a_word(
            origen,
            destino
        )

        return resultado
