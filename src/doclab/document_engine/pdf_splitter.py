
"""
Motor de division y extraccion de paginas PDF.

Primera funcionalidad:
- Extraer un rango continuo de paginas.
- Validar documento y rango solicitado.
- Proteger documentos originales.
- Evitar sobrescritura del destino.
- Limpiar archivos temporales ante errores.
"""

import os
import tempfile

from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf



def extraer_rango_pdf(
    ruta_origen,
    ruta_destino,
    pagina_inicio,
    pagina_fin
):
    """
    Extrae un rango de paginas de un PDF.

    Los numeros de pagina comienzan en 1.

    Retorna:
        str: Ruta del PDF generado.
    """

    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # 1. Validar los numeros de pagina.
    if (
        type(pagina_inicio) is not int
        or type(pagina_fin) is not int
    ):
        raise ValueError(
            "Los numeros de pagina deben ser enteros."
        )

    if pagina_inicio < 1:
        raise ValueError(
            "La pagina inicial debe ser mayor o igual a 1."
        )

    if pagina_fin < pagina_inicio:
        raise ValueError(
            "La pagina final no puede ser menor "
            "que la pagina inicial."
        )

    # 2. Validar el PDF original.
    total_paginas = validar_pdf(origen)

    if pagina_fin > total_paginas:
        raise ValueError(
            "El rango solicitado supera la cantidad "
            "de paginas del documento."
        )

    # 3. Validar el destino.
    if destino.suffix.lower() != ".pdf":
        raise ValueError(
            "El documento de destino debe ser PDF."
        )

    if origen.resolve() == destino.resolve():
        raise ValueError(
            "El destino no puede ser el archivo original."
        )

    if destino.exists():
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # 4. Crear archivo temporal.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_division_",
        suffix=".pdf",
        dir=destino.parent
    )

    os.close(descriptor)

    temporal = Path(ruta_temporal)

    try:
        # 5. Extraer las paginas solicitadas.
        with pymupdf.open(str(origen)) as documento_origen:
            with pymupdf.open() as documento_final:

                documento_final.insert_pdf(
                    documento_origen,
                    from_page=pagina_inicio - 1,
                    to_page=pagina_fin - 1
                )

                documento_final.save(str(temporal))

        # 6. Validar el PDF generado.
        paginas_esperadas = (
            pagina_fin - pagina_inicio + 1
        )

        paginas_generadas = validar_pdf(temporal)

        if paginas_generadas != paginas_esperadas:
            raise RuntimeError(
                "El PDF generado no contiene "
                "la cantidad de paginas esperada."
            )

        # 7. Publicar sin sobrescribir.
        try:
            os.link(temporal, destino)

        except FileExistsError:
            raise FileExistsError(
                "El archivo de destino ya existe."
            )

        except OSError as error:
            raise OSError(
                "No fue posible publicar el documento. "
                "Comprueba los permisos y la compatibilidad "
                "con enlaces fisicos."
            ) from error

        return str(destino)

    finally:
        # 8. Limpiar el archivo temporal.
        temporal.unlink(missing_ok=True)

def extraer_paginas_pdf(
    ruta_origen,
    ruta_destino,
    paginas
):
    """
    Extrae paginas especificas de un PDF.

    Los numeros comienzan en 1.
    Respeta el orden recibido y rechaza duplicados.

    Ejemplo:
        paginas = [1, 4, 8]

    Retorna:
        str: Ruta del documento generado.
    """

    origen = Path(ruta_origen)
    destino = Path(ruta_destino)

    # 1. Validar la seleccion.
    if not isinstance(paginas, (list, tuple)):
        raise ValueError(
            "Las paginas deben entregarse en una lista."
        )

    if not paginas:
        raise ValueError(
            "Debes seleccionar al menos una pagina."
        )

    for numero in paginas:
        if type(numero) is not int:
            raise ValueError(
                "Los numeros de pagina deben ser enteros."
            )

    if len(paginas) != len(set(paginas)):
        raise ValueError(
            "La seleccion contiene paginas repetidas."
        )

    # 2. Validar el documento original.
    total_paginas = validar_pdf(origen)

    for numero in paginas:
        if numero < 1 or numero > total_paginas:
            raise ValueError(
                f"La pagina {numero} esta fuera "
                "del rango del documento."
            )

    # 3. Validar el destino.
    if destino.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de destino debe ser PDF."
        )

    if origen.resolve() == destino.resolve():
        raise ValueError(
            "El destino no puede ser el archivo original."
        )

    if destino.exists():
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # 4. Crear el archivo temporal.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_paginas_",
        suffix=".pdf",
        dir=destino.parent
    )

    os.close(descriptor)
    temporal = Path(ruta_temporal)

    try:
        # 5. Copiar las paginas seleccionadas.
        with pymupdf.open(str(origen)) as documento_origen:
            with pymupdf.open() as documento_final:

                for numero in paginas:
                    indice = numero - 1

                    documento_final.insert_pdf(
                        documento_origen,
                        from_page=indice,
                        to_page=indice
                    )

                documento_final.save(str(temporal))

        # 6. Comprobar el resultado.
        paginas_generadas = validar_pdf(temporal)

        if paginas_generadas != len(paginas):
            raise RuntimeError(
                "La cantidad de paginas generadas "
                "no coincide con la seleccion."
            )

        # 7. Publicar sin sobrescribir.
        try:
            os.link(temporal, destino)

        except FileExistsError:
            raise FileExistsError(
                "El documento de destino ya existe."
            )

        except OSError as error:
            raise OSError(
                "No fue posible publicar el PDF. "
                "Comprueba los permisos y el sistema "
                "de archivos."
            ) from error

        return str(destino)

    finally:
        # 8. Limpiar el temporal.
        temporal.unlink(missing_ok=True)

def separar_paginas_pdf(ruta_origen, carpeta_destino):
    """
    Separa todas las paginas de un PDF.

    Genera un archivo independiente por pagina
    dentro de una carpeta existente.

    No sobrescribe documentos y elimina las
    salidas creadas si falla la publicacion.

    Retorna:
        list[str]: Rutas de los PDF generados.
    """

    origen = Path(ruta_origen)
    carpeta = Path(carpeta_destino)

    # 1. Validar el documento original.
    total_paginas = validar_pdf(origen)

    # 2. Comprobar la carpeta de salida.
    if not carpeta.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # 3. Preparar los nombres de salida.
    cantidad_digitos = max(
        3,
        len(str(total_paginas))
    )

    destinos = []

    for numero in range(1, total_paginas + 1):
        nombre = (
            f"{origen.stem}_pagina_"
            f"{numero:0{cantidad_digitos}d}.pdf"
        )

        destino = carpeta / nombre

        if destino.exists() or destino.is_symlink():
            raise FileExistsError(
                f"Ya existe un archivo de salida: {nombre}"
            )

        destinos.append(destino)

    # 4. Crear una carpeta temporal.
    with tempfile.TemporaryDirectory(
        prefix="doclab_division_",
        dir=carpeta
    ) as carpeta_temporal:

        temporal = Path(carpeta_temporal)
        archivos_preparados = []

        # 5. Generar un PDF por pagina.
        with pymupdf.open(str(origen)) as documento_origen:

            for indice in range(total_paginas):
                ruta_temporal = (
                    temporal / destinos[indice].name
                )

                with pymupdf.open() as documento_nuevo:
                    documento_nuevo.insert_pdf(
                        documento_origen,
                        from_page=indice,
                        to_page=indice
                    )

                    documento_nuevo.save(
                        str(ruta_temporal)
                    )

                # 6. Verificar cada resultado.
                paginas_generadas = validar_pdf(
                    ruta_temporal
                )

                if paginas_generadas != 1:
                    raise RuntimeError(
                        "Uno de los archivos generados "
                        "no contiene exactamente una pagina."
                    )

                archivos_preparados.append(
                    ruta_temporal
                )

        # 7. Publicar los archivos.
        archivos_publicados = []

        try:
            for archivo_temporal, destino in zip(
                archivos_preparados,
                destinos
            ):
                os.link(
                    archivo_temporal,
                    destino
                )

                archivos_publicados.append(
                    destino
                )

        except Exception:
            # Retirar solamente los archivos
            # publicados por esta operacion.
            for archivo in archivos_publicados:
                archivo.unlink(missing_ok=True)

            raise

    # 8. Entregar las rutas finales.
    return [
        str(destino)
        for destino in destinos
    ]
