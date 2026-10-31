
"""
Prueba de integracion real del motor OCR de DocLab.

Genera un PDF con una imagen de texto y comprueba
que el motor OCR pueda reconocer su contenido.
"""

import pymupdf

from doclab.document_engine.ocr_engine import (
    reconocer_texto_pagina,
    verificar_recursos_ocr,
)


def test_ocr_real_imagen_con_texto(tmp_path):
    # 1. Verificar los idiomas OCR disponibles.
    verificar_recursos_ocr()

    # 2. Definir las rutas temporales.
    ruta_pdf = tmp_path / "documento_escaneado.pdf"

    # 3. Crear una pagina con texto digital temporal.
    with pymupdf.open() as documento_origen:
        pagina = documento_origen.new_page(
            width=600,
            height=200
        )

        pagina.insert_text(
            (35, 110),
            "DOC LAB PRUEBA OCR 2026",
            fontsize=28
        )

        # 4. Convertir la pagina a una imagen.
        imagen = pagina.get_pixmap(
            dpi=300,
            alpha=False
        )

        # 5. Crear otro PDF que solo contenga
        # la imagen, sin texto digital.
        with pymupdf.open() as documento_escaneado:
            pagina_escaneada = documento_escaneado.new_page(
                width=600,
                height=200
            )

            pagina_escaneada.insert_image(
                pagina_escaneada.rect,
                pixmap=imagen
            )

            documento_escaneado.save(str(ruta_pdf))

    # 6. Confirmar que no hay texto seleccionable.
    with pymupdf.open(str(ruta_pdf)) as documento:
        texto_original = documento[0].get_text("text")

        assert texto_original.strip() == ""

    # 7. Ejecutar nuestro motor OCR real.
    resultado = reconocer_texto_pagina(
        ruta_archivo=ruta_pdf,
        numero_pagina=1,
        idioma="spa+eng",
        dpi=300,
        completo=True
    )

    # 8. Normalizar espacios y mayusculas.
    texto_reconocido = " ".join(
        resultado.texto.upper().split()
    )

    # 9. Comprobar el reconocimiento.
    assert "DOC" in texto_reconocido
    assert "LAB" in texto_reconocido
    assert "PRUEBA" in texto_reconocido
    assert "OCR" in texto_reconocido
    assert "2026" in texto_reconocido
