
"""
Trabajador para operaciones de division PDF.

Ejecuta el servicio de division en un hilo
secundario, sin bloquear la interfaz PySide6.
"""

from PySide6.QtCore import QThread, Signal

from doclab.services.pdf_split_service import (
    ServicioDivisionPDF,
)


class TrabajadorDivisionPDF(QThread):
    """
    Ejecuta una de las tres modalidades
    de division de archivos PDF.

    Senales:
        division_exitosa(object):
            Lista de rutas generadas.

        division_fallida(str):
            Mensaje de error.
    """

    division_exitosa = Signal(object)
    division_fallida = Signal(str)

    MODOS_VALIDOS = (
        "rango",
        "paginas",
        "todas",
    )

    def __init__(
        self,
        modo,
        ruta_origen,
        ruta_destino,
        pagina_inicio=None,
        pagina_fin=None,
        paginas=None,
        parent=None,
    ):
        super().__init__(parent)

        self.modo = modo
        self.ruta_origen = ruta_origen
        self.ruta_destino = ruta_destino
        self.pagina_inicio = pagina_inicio
        self.pagina_fin = pagina_fin

        # Copiamos la seleccion para evitar que
        # cambie durante la operacion.
        self.paginas = (
            list(paginas)
            if isinstance(paginas, (list, tuple))
            else paginas
        )

    def run(self):
        """
        Ejecuta la division y comunica el resultado.

        Este metodo se ejecuta en un hilo secundario
        cuando se utiliza start().
        """

        try:
            servicio = ServicioDivisionPDF()

            if self.modo == "rango":
                resultado = servicio.extraer_rango(
                    self.ruta_origen,
                    self.ruta_destino,
                    self.pagina_inicio,
                    self.pagina_fin,
                )

            elif self.modo == "paginas":
                resultado = servicio.extraer_paginas(
                    self.ruta_origen,
                    self.ruta_destino,
                    self.paginas,
                )

            elif self.modo == "todas":
                resultado = servicio.separar_todas(
                    self.ruta_origen,
                    self.ruta_destino,
                )

            else:
                raise ValueError(
                    f"Modalidad de division no valida: "
                    f"{self.modo}"
                )

            # Normalizamos el resultado para que
            # siempre sea una lista de rutas.
            if isinstance(resultado, (str, bytes)):
                rutas_generadas = [str(resultado)]
            else:
                rutas_generadas = [
                    str(ruta)
                    for ruta in resultado
                ]

            self.division_exitosa.emit(rutas_generadas)

        except Exception as error:
            self.division_fallida.emit(str(error))
