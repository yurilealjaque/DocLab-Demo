
"""
Motor de compresión PDF sin pérdida intencional.

Responsabilidades:
- Validar origen y destino.
- Evitar modificar el documento original.
- Rechazar PDF con firmas digitales detectables.
- Optimizar las estructuras internas del PDF.
- Verificar propiedades esenciales del resultado.
- Publicar únicamente si existe ahorro de espacio.
- Limpiar archivos temporales.

No depende de PySide6.
"""

import os
import re
import tempfile

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf


class SinReduccionError(Exception):
    """No se consiguió reducir el tamaño del PDF."""


class DocumentoFirmadoError(Exception):
    """El PDF contiene posibles firmas digitales."""


@dataclass(frozen=True)
class ResultadoCompresion:
    """Información sobre un PDF comprimido."""

    ruta_destino: str
    tamano_original: int
    tamano_final: int
    paginas: int

    @property
    def bytes_ahorrados(self):
        return self.tamano_original - self.tamano_final

    @property
    def porcentaje_reduccion(self):
        if self.tamano_original == 0:
            return 0.0

        return (
            self.bytes_ahorrados
            / self.tamano_original
            * 100
        )


def detectar_firmas(documento):
    """
    Detecta campos y objetos de firma reconocibles.

    Es una medida preventiva, no un verificador
    criptográfico completo de firmas digitales.
    """

    patron_firma = re.compile(
        r"/(?:FT|Type)\s*/Sig\b"
    )

    for numero_objeto in range(1, documento.xref_length()):
        try:
            contenido = documento.xref_object(
                numero_objeto,
                compressed=False
            )
        except (ValueError, RuntimeError):
            # Ante objetos que no podemos inspeccionar,
            # rechazamos preventivamente el documento.
            raise DocumentoFirmadoError(
                "No fue posible inspeccionar todos "
                "los objetos del documento."
            )

        if patron_firma.search(contenido):
            return True

    return False


def obtener_resumen(documento):
    """
    Obtiene propiedades básicas del documento
    para comparar el origen con el resultado.

    No garantiza equivalencia visual absoluta.
    """

    resumen = []

    for pagina in documento:
        resumen.append(
            (
                round(pagina.rect.width, 3),
                round(pagina.rect.height, 3),
                pagina.rotation,
                pagina.get_text("text"),
                len(pagina.get_links()),
                len(list(pagina.annots() or [])),
                len(list(pagina.widgets() or [])),
            )
        )

    return resumen


def comprimir_pdf(ruta_origen, ruta_destino):
    """
    Comprime un PDF sin modificar su original.

    Retorna:
        ResultadoCompresion

    Lanza, entre otras:
        FileNotFoundError
        FileExistsError
        ValueError
        DocumentoFirmadoError
        SinReduccionError
        RuntimeError
    """

    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # 1. Validar el documento original.
    paginas_originales = validar_pdf(origen)

    # 2. Validar el destino.
    if destino.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de destino debe ser PDF."
        )

    if origen.resolve() == destino.resolve():
        raise ValueError(
            "El destino no puede ser el documento original."
        )

    if destino.exists() or destino.is_symlink():
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    tamano_original = origen.stat().st_size

    # 3. Preparar el archivo temporal.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_compresion_",
        suffix=".pdf",
        dir=destino.parent
    )

    os.close(descriptor)
    temporal = Path(ruta_temporal)

    try:
        # 4. Abrir y optimizar el documento.
        with pymupdf.open(str(origen)) as documento:

            if detectar_firmas(documento):
                raise DocumentoFirmadoError(
                    "El documento contiene una posible "
                    "firma digital y no puede comprimirse "
                    "con esta modalidad."
                )

            resumen_original = obtener_resumen(
                documento
            )

            documento.save(
                str(temporal),
                garbage=3,
                deflate=True,
                use_objstms=1,
                clean=False,
                incremental=False,
                linear=False
            )

        # 5. Revisar el tamaño obtenido.
        tamano_final = temporal.stat().st_size

        if tamano_final >= tamano_original:
            raise SinReduccionError(
                "El documento ya está optimizado "
                "o no se obtuvo una reducción de tamaño."
            )

        # 6. Validar el documento generado.
        paginas_generadas = validar_pdf(temporal)

        if paginas_generadas != paginas_originales:
            raise RuntimeError(
                "El resultado no conserva "
                "la cantidad de páginas."
            )

        with pymupdf.open(str(temporal)) as documento_final:
            resumen_final = obtener_resumen(
                documento_final
            )

        if resumen_original != resumen_final:
            raise RuntimeError(
                "Se detectaron diferencias en propiedades "
                "esenciales del PDF comprimido."
            )

        # 7. Publicar sin sobrescribir.
        try:
            os.link(temporal, destino)

        except FileExistsError:
            raise FileExistsError(
                "Otro archivo ocupa el destino."
            )

        except OSError as error:
            raise OSError(
                "No fue posible publicar el PDF. "
                "Comprueba los permisos y la compatibilidad "
                "del sistema de archivos."
            ) from error

        # 8. Devolver el resultado.
        return ResultadoCompresion(
            ruta_destino=str(destino),
            tamano_original=tamano_original,
            tamano_final=tamano_final,
            paginas=paginas_generadas
        )

    finally:
        # 9. Limpiar el temporal en todos los casos.
        temporal.unlink(missing_ok=True)
