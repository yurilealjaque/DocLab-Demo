"""
Prueba de integracion visual de DocLab.

Comprueba el flujo completo:

PDF -> OCR -> Extraccion de imagenes -> Word

El PDF contiene paginas digitales, mixtas
y escaneadas.
"""

import pymupdf

from docx import Document

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr
)

from doclab.document_engine.pdf_image_extractor import (
    extraer_imagenes_pdf
)

from doclab.document_engine.ocr_word_visual import (
    exportar_word_con_imagenes
)


def crear_imagen_con_texto(texto):
    """
    Crea una imagen PNG que contiene palabras.

    El contenido de la imagen no conserva
    texto digital seleccionable.
    """

    with pymupdf.open() as documento:

        pagina = documento.new_page(
            width=600,
            height=200
        )

        pagina.insert_text(
            (35, 110),
            texto,
            fontsize=28
        )

        imagen = pagina.get_pixmap(
            dpi=300,
            alpha=False
        )

        return imagen.tobytes("png")


def test_conversion_visual_completa(tmp_path):

    # 1. Comprobar modelos OCR instalados.
    verificar_recursos_ocr()

    # 2. Definir archivos temporales.
    ruta_pdf = tmp_path / "documento_visual.pdf"
    ruta_word = tmp_path / "documento_visual.docx"

    # 3. Preparar las imagenes.
    imagen_mixta = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    # 4. Crear un PDF de tres paginas.
    with pymupdf.open() as documento:

        # Pagina 1: solo texto digital.
        pagina_uno = documento.new_page(
            width=600,
            height=400
        )

        pagina_uno.insert_text(
            (50, 100),
            "DOCUMENTO DIGITAL DOCLAB",
            fontsize=22
        )

        # Pagina 2: texto digital e imagen.
        pagina_dos = documento.new_page(
            width=600,
            height=500
        )

        pagina_dos.insert_text(
            (50, 60),
            "ENCABEZADO DIGITAL",
            fontsize=20
        )

        pagina_dos.insert_image(
            pymupdf.Rect(20, 130, 580, 320),
            stream=imagen_mixta
        )

        # Pagina 3: imagen escaneada completa.
        pagina_tres = documento.new_page(
            width=600,
            height=200
        )

        pagina_tres.insert_image(
            pagina_tres.rect,
            stream=imagen_escaneada
        )

        documento.save(str(ruta_pdf))

    # 5. Comprobar que la tercera pagina
    # realmente no contiene texto digital.
    with pymupdf.open(str(ruta_pdf)) as documento:

        assert documento[2].get_text("text").strip() == ""

    # 6. Procesar el documento mediante OCR.
    resultado_ocr = procesar_documento_ocr(
        ruta_archivo=ruta_pdf,
        idioma="spa+eng",
        dpi=300
    )

    assert resultado_ocr.total_paginas == 3

    assert tuple(
        pagina.metodo
        for pagina in resultado_ocr.paginas
    ) == (
        "digital",
        "ocr_parcial",
        "ocr_completo"
    )

    # 7. Recuperar las imagenes del PDF.
    resultado_imagenes = extraer_imagenes_pdf(
        ruta_pdf
    )

    assert resultado_imagenes.total_paginas == 3
    assert len(resultado_imagenes.imagenes) == 2

    # 8. Generar el Word con texto e imagenes.
    ruta_generada = exportar_word_con_imagenes(
        resultado_ocr=resultado_ocr,
        resultado_imagenes=resultado_imagenes,
        ruta_destino=ruta_word
    )

    assert ruta_generada == str(ruta_word)
    assert ruta_word.is_file()

    # 9. Abrir el Word generado.
    documento_word = Document(str(ruta_word))

    contenido = " ".join(
        parrafo.text
        for parrafo in documento_word.paragraphs
    )

    contenido = " ".join(
        contenido.upper().split()
    )

    # 10. Comprobar texto digital.
    assert "DOCUMENTO DIGITAL DOCLAB" in contenido
    assert "ENCABEZADO DIGITAL" in contenido

    # 11. Comprobar OCR de imagen incrustada.
    assert "CODIGO" in contenido
    assert "IMAGEN" in contenido
    assert "5678" in contenido

    # 12. Comprobar OCR de pagina escaneada.
    assert "FACTURA" in contenido
    assert "DOCLAB" in contenido
    assert "2026" in contenido

    # 13. Comprobar las imagenes del Word.
    #
    # Se conserva la imagen de la pagina mixta.
    # No se repite la imagen del escaneo completo.
    assert len(documento_word.inline_shapes) == 1

