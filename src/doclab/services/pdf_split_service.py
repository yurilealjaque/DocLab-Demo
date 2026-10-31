
"""
Servicio de division de documentos PDF.

Coordina las operaciones del motor documental
sin depender de los componentes de la interfaz.
"""

from doclab.document_engine.pdf_splitter import (
    extraer_rango_pdf,
    extraer_paginas_pdf,
    separar_paginas_pdf,
)


class ServicioDivisionPDF:
    """
    Servicio encargado de las operaciones
    de division y extraccion de paginas PDF.
    """

    def extraer_rango(
        self,
        ruta_origen,
        ruta_destino,
        pagina_inicio,
        pagina_fin
    ):
        """
        Extrae un rango continuo de paginas.

        Ejemplo:
            Paginas 3 a 7.

        Retorna:
            str: Ruta del PDF generado.
        """

        return extraer_rango_pdf(
            ruta_origen,
            ruta_destino,
            pagina_inicio,
            pagina_fin
        )

    def extraer_paginas(
        self,
        ruta_origen,
        ruta_destino,
        paginas
    ):
        """
        Extrae paginas especificas.

        Ejemplo:
            [1, 4, 8].

        Retorna:
            str: Ruta del PDF generado.
        """

        return extraer_paginas_pdf(
            ruta_origen,
            ruta_destino,
            paginas
        )

    def separar_todas(
        self,
        ruta_origen,
        carpeta_destino
    ):
        """
        Genera un PDF independiente
        por cada pagina del original.

        Retorna:
            list[str]: Rutas de los archivos generados.
        """

        return separar_paginas_pdf(
            ruta_origen,
            carpeta_destino
        )
