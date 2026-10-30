
from doclab.document_engine.pdf_validator import (
    validar_pdf
)

from doclab.document_engine.pdf_to_word import (
    convertir_pdf_a_word
)


class ServicioConversion:

    def convertir(self, origen, destino):
        # Primero validar el documento.
        validar_pdf(origen)

        # Si la validacion es exitosa,
        # comenzar la conversion.
        resultado = convertir_pdf_a_word(
            origen,
            destino
        )

        return resultado
