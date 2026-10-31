import os
import tempfile

from pathlib import Path

import pymupdf

from doclab.document_engine.pdf_validator import validar_pdf


def unir_archivos_pdf(rutas_origen, ruta_destino):
    """
    Une dos o más archivos PDF en el orden recibido.

    Retorna:
        str: Ruta del PDF generado correctamente.
    """

    # 1. Comprobar la cantidad de archivos.
    rutas = [Path(ruta) for ruta in rutas_origen]

    if len(rutas) < 2:
        raise ValueError(
            "Debes seleccionar al menos dos archivos PDF."
        )

    destino = Path(ruta_destino)

    # 2. Validar la ruta de salida.
    if destino.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo de destino debe tener extensión PDF."
        )

    if destino.exists():
        raise FileExistsError(
            "El archivo de destino ya existe."
        )

    if not destino.parent.is_dir():
        raise FileNotFoundError(
            "La carpeta de destino no existe."
        )

    # 3. Validar todos los documentos de entrada.
    total_paginas = 0

    for ruta in rutas:
        total_paginas += validar_pdf(ruta)

        if ruta.resolve() == destino.resolve():
            raise ValueError(
                "El destino no puede coincidir con un origen."
            )

    # 4. Crear un PDF temporal en la carpeta de destino.
    descriptor, ruta_temporal = tempfile.mkstemp(
        prefix="doclab_union_",
        suffix=".pdf",
        dir=destino.parent
    )

    os.close(descriptor)
    temporal = Path(ruta_temporal)

    try:
        # 5. Construir el documento unido página por página.
        with pymupdf.open() as documento_final:

            for ruta in rutas:
                with pymupdf.open(str(ruta)) as documento_origen:

                    for numero_pagina in range(
                        documento_origen.page_count
                    ):
                        pagina_origen = documento_origen.load_page(
                            numero_pagina
                        )

                        rect = pagina_origen.rect

                        pagina_nueva = documento_final.new_page(
                            width=rect.width,
                            height=rect.height
                        )

                        pagina_nueva.show_pdf_page(
                            pagina_nueva.rect,
                            documento_origen,
                            numero_pagina
                        )

            documento_final.save(
                str(temporal),
                garbage=4,
                clean=True,
                deflate=True
            )

        # 6. Verificar el PDF generado.
        paginas_generadas = validar_pdf(temporal)

        if paginas_generadas != total_paginas:
            raise RuntimeError(
                "El PDF generado no tiene la cantidad "
                "de páginas esperada."
            )

        # 7. Publicar sin sobrescribir.
        try:
            os.link(temporal, destino)

        except FileExistsError:
            raise FileExistsError(
                "Ya existe un archivo en el destino."
            )

        except OSError as error:
            raise OSError(
                "No se pudo publicar el PDF. "
                "Comprueba los permisos y la compatibilidad "
                "con enlaces físicos."
            ) from error

        return str(destino)

    finally:
        # 8. Eliminar el archivo temporal.
        temporal.unlink(missing_ok=True)