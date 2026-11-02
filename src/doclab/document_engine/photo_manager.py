
import os
from pathlib import Path

from doclab.document_engine.image_validator import (
    InformacionImagen,
    validar_imagen,
)


class ErrorGestionFotografias(Exception):
    """Error general al gestionar fotografias."""


class FotografiaDuplicadaError(ErrorGestionFotografias):
    """La fotografia ya esta incorporada a la coleccion."""


class FotografiaNoEncontradaError(ErrorGestionFotografias):
    """La fotografia solicitada no esta en la coleccion."""


class GestorFotografias:
    """
    Gestiona una coleccion ordenada de fotografias.

    No modifica, mueve ni elimina archivos originales.
    """

    def __init__(self):
        self._fotografias: list[InformacionImagen] = []

    @staticmethod
    def _normalizar_ruta(ruta_archivo) -> str:
        """
        Normaliza una ruta para comparar archivos.

        En Windows evita diferencias por mayusculas,
        minusculas y rutas relativas.
        """
        ruta = Path(ruta_archivo).resolve()
        return os.path.normcase(str(ruta))

    def obtener_fotografias(self) -> tuple[InformacionImagen, ...]:
        """Devuelve una vista inmutable de la coleccion."""
        return tuple(self._fotografias)

    def cantidad(self) -> int:
        """Devuelve la cantidad de fotografias."""
        return len(self._fotografias)

    def agregar_fotografia(self, ruta_archivo) -> InformacionImagen:
        """
        Valida y agrega una fotografia al final.

        No permite agregar dos veces la misma ruta.
        """
        ruta_normalizada = self._normalizar_ruta(ruta_archivo)

        for fotografia in self._fotografias:
            if self._normalizar_ruta(fotografia.ruta) == ruta_normalizada:
                raise FotografiaDuplicadaError(
                    "La fotografia ya fue agregada."
                )

        informacion = validar_imagen(ruta_archivo)

        self._fotografias.append(informacion)
        return informacion

    def agregar_fotografias(self, rutas_archivos) -> int:
        """
        Agrega multiples fotografias.

        La operacion es todo o nada:
        si existe un error, no agrega ninguna.

        Retorna la cantidad incorporada.
        """
        rutas = list(rutas_archivos)

        rutas_existentes = {
            self._normalizar_ruta(fotografia.ruta)
            for fotografia in self._fotografias
        }

        nuevas_fotografias = []
        rutas_nuevas = set()

        for ruta_archivo in rutas:
            ruta_normalizada = self._normalizar_ruta(ruta_archivo)

            if (
                ruta_normalizada in rutas_existentes
                or ruta_normalizada in rutas_nuevas
            ):
                raise FotografiaDuplicadaError(
                    "La seleccion contiene una fotografia duplicada."
                )

            informacion = validar_imagen(ruta_archivo)

            nuevas_fotografias.append(informacion)
            rutas_nuevas.add(ruta_normalizada)

        self._fotografias.extend(nuevas_fotografias)

        return len(nuevas_fotografias)

    def quitar_fotografia(self, indice: int) -> InformacionImagen:
        """
        Quita una fotografia de la coleccion.

        No elimina el archivo del disco.
        """
        self._validar_indice(indice)
        return self._fotografias.pop(indice)

    def subir_fotografia(self, indice: int) -> bool:
        """
        Sube una fotografia una posicion.

        Retorna False si ya esta en la primera posicion.
        """
        self._validar_indice(indice)

        if indice == 0:
            return False

        self._fotografias[indice - 1], self._fotografias[indice] = (
            self._fotografias[indice],
            self._fotografias[indice - 1],
        )

        return True

    def bajar_fotografia(self, indice: int) -> bool:
        """
        Baja una fotografia una posicion.

        Retorna False si ya esta en la ultima posicion.
        """
        self._validar_indice(indice)

        if indice == len(self._fotografias) - 1:
            return False

        self._fotografias[indice], self._fotografias[indice + 1] = (
            self._fotografias[indice + 1],
            self._fotografias[indice],
        )

        return True

    def vaciar(self) -> None:
        """Limpia la coleccion, sin eliminar archivos."""
        self._fotografias.clear()

    def _validar_indice(self, indice: int) -> None:
        """Comprueba que un indice corresponda a una fotografia."""
        if type(indice) is not int:
            raise TypeError(
                "El indice debe ser un numero entero."
            )

        if indice < 0 or indice >= len(self._fotografias):
            raise FotografiaNoEncontradaError(
                "La fotografia seleccionada no existe."
            )
