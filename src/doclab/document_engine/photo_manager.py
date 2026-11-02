"""Gestión ordenada de imágenes, rotaciones y ajustes no destructivos."""

import os
from pathlib import Path

from doclab.document_engine.image_adjustments import _validar_ajuste

from doclab.document_engine.image_validator import (
    InformacionImagen,
    validar_imagen,
)


class ErrorGestionFotografias(Exception):
    """Error general al gestionar fotografías."""


class FotografiaDuplicadaError(ErrorGestionFotografias):
    """La fotografía ya está incorporada a la colección."""


class FotografiaNoEncontradaError(ErrorGestionFotografias):
    """La fotografía solicitada no está en la colección."""


class GestorFotografias:
    """Colección ordenada de fotografías, sin modificar los originales.

    Las rotaciones y los ajustes se almacenan en memoria por ruta normalizada.
    Rotaciones: 0, 90, 180 y 270 grados horarios.
    Brillo y contraste: valores enteros entre -100 y 100.
    """

    def __init__(self):
        self._fotografias: list[InformacionImagen] = []
        self._rotaciones: dict[str, int] = {}
        self._ajustes: dict[str, tuple[int, int]] = {}

    @staticmethod
    def _normalizar_ruta(ruta_archivo) -> str:
        """Normaliza rutas; en Windows también normaliza mayúsculas."""
        ruta = Path(ruta_archivo).resolve()
        return os.path.normcase(str(ruta))

    def obtener_fotografias(self) -> tuple[InformacionImagen, ...]:
        """Devuelve una vista inmutable de la colección ordenada."""
        return tuple(self._fotografias)

    def cantidad(self) -> int:
        """Devuelve la cantidad de fotografías."""
        return len(self._fotografias)

    def agregar_fotografia(self, ruta_archivo) -> InformacionImagen:
        """Valida e incorpora una fotografía, rechazando duplicados."""
        clave = self._normalizar_ruta(ruta_archivo)

        for fotografia in self._fotografias:
            if self._normalizar_ruta(fotografia.ruta) == clave:
                raise FotografiaDuplicadaError(
                    "La fotografía ya fue agregada."
                )

        informacion = validar_imagen(ruta_archivo)
        self._fotografias.append(informacion)
        self._rotaciones[clave] = 0
        self._ajustes[clave] = (0, 0)
        return informacion

    def agregar_fotografias(self, rutas_archivos) -> int:
        """Agrega un lote de forma atómica: ante un error no cambia nada."""
        rutas = list(rutas_archivos)
        rutas_existentes = {
            self._normalizar_ruta(fotografia.ruta)
            for fotografia in self._fotografias
        }
        nuevas_fotografias = []
        rutas_nuevas = set()

        for ruta_archivo in rutas:
            clave = self._normalizar_ruta(ruta_archivo)
            if clave in rutas_existentes or clave in rutas_nuevas:
                raise FotografiaDuplicadaError(
                    "La selección contiene una fotografía duplicada."
                )
            informacion = validar_imagen(ruta_archivo)
            nuevas_fotografias.append(informacion)
            rutas_nuevas.add(clave)

        self._fotografias.extend(nuevas_fotografias)
        for clave in rutas_nuevas:
            self._rotaciones[clave] = 0
            self._ajustes[clave] = (0, 0)
        return len(nuevas_fotografias)

    def quitar_fotografia(self, indice: int) -> InformacionImagen:
        """Quita la fotografía y su rotación; no borra el archivo."""
        self._validar_indice(indice)
        fotografia = self._fotografias.pop(indice)
        clave = self._normalizar_ruta(fotografia.ruta)
        self._rotaciones.pop(clave, None)
        self._ajustes.pop(clave, None)
        return fotografia

    def subir_fotografia(self, indice: int) -> bool:
        """Sube la fotografía una posición, sin perder su rotación."""
        self._validar_indice(indice)
        if indice == 0:
            return False
        self._fotografias[indice - 1], self._fotografias[indice] = (
            self._fotografias[indice],
            self._fotografias[indice - 1],
        )
        return True

    def bajar_fotografia(self, indice: int) -> bool:
        """Baja la fotografía una posición, sin perder su rotación."""
        self._validar_indice(indice)
        if indice == len(self._fotografias) - 1:
            return False
        self._fotografias[indice], self._fotografias[indice + 1] = (
            self._fotografias[indice + 1],
            self._fotografias[indice],
        )
        return True

    def obtener_rotacion(self, indice: int) -> int:
        """Obtiene grados de giro horario de la imagen indicada."""
        self._validar_indice(indice)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        return self._rotaciones[clave]

    def rotar_derecha(self, indice: int) -> int:
        """Suma 90° horarios y devuelve la rotación resultante."""
        self._validar_indice(indice)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        self._rotaciones[clave] = (self._rotaciones[clave] + 90) % 360
        return self._rotaciones[clave]

    def rotar_izquierda(self, indice: int) -> int:
        """Resta 90° horarios y devuelve la rotación resultante."""
        self._validar_indice(indice)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        self._rotaciones[clave] = (self._rotaciones[clave] - 90) % 360
        return self._rotaciones[clave]

    def obtener_ajustes(self, indice: int) -> tuple[int, int]:
        """Retorna (brillo, contraste) de una imagen de la colección."""
        self._validar_indice(indice)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        return self._ajustes[clave]

    def establecer_ajustes(
        self,
        indice: int,
        brillo: int,
        contraste: int,
    ) -> tuple[int, int]:
        """Guarda ambos ajustes de forma atómica, sin modificar el archivo."""
        self._validar_indice(indice)
        _validar_ajuste("brillo", brillo)
        _validar_ajuste("contraste", contraste)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        self._ajustes[clave] = (brillo, contraste)
        return self._ajustes[clave]

    def restablecer_ajustes(self, indice: int) -> tuple[int, int]:
        """Devuelve brillo y contraste a cero; conserva la rotación."""
        self._validar_indice(indice)
        clave = self._normalizar_ruta(self._fotografias[indice].ruta)
        self._ajustes[clave] = (0, 0)
        return self._ajustes[clave]

    def vaciar(self) -> None:
        """Limpia colección, rotaciones y ajustes, sin borrar archivos."""
        self._fotografias.clear()
        self._rotaciones.clear()
        self._ajustes.clear()

    def _validar_indice(self, indice: int) -> None:
        """Valida tipo y rango del índice."""
        if type(indice) is not int:
            raise TypeError("El índice debe ser un número entero.")
        if indice < 0 or indice >= len(self._fotografias):
            raise FotografiaNoEncontradaError(
                "La fotografía seleccionada no existe."
            )
