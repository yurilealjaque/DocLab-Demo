
"""
Prueba de integracion completa de DocLab.

Verifica el flujo:

PDF digital y escaneado
        |
        v
Procesamiento OCR
        |
        v
Exportacion a Word
        |
        v
Documento DOCX editable
"""

import pymupdf

from docx import Document

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.ocr_word_export import (
    exportar_ocr_a_word
)

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr
)


def crear_imagen_con_texto(texto):
    """
    Genera una imagen PNG que contiene texto.

    La imagen no conserva una capa de
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


def test_conversion_pdf_ocr_a_word_real(tmp_path):

    # 1. Verificar los modelos OCR.
    verificar_recursos_ocr()

    # 2. Definir archivos temporales.
    ruta_pdf = tmp_path / "documento_original.pdf"
    ruta_word = tmp_path / "documento_convertido.docx"

    # 3. Crear una imagen con texto.
    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    # 4. Construir el PDF original.
    with pymupdf.open() as documento:

        # Primera pagina: texto digital.
        pagina_uno = documento.new_page(
            width=600,
            height=400
        )

        pagina_uno.insert_text(
            (50, 100),
            "DOCUMENTO DIGITAL DOCLAB",
            fontsize=22
        )

        # Segunda pagina: imagen escaneada.
        pagina_dos = documento.new_page(
            width=600,
            height=200
        )

        pagina_dos.insert_image(
            pagina_dos.rect,
            stream=imagen_escaneada
        )

        documento.save(str(ruta_pdf))

    # 5. Comprobar que la pagina escaneada
    # no tiene texto extraible originalmente.
    with pymupdf.open(str(ruta_pdf)) as documento:

        assert documento[1].get_text("text").strip() == ""

    # 6. Ejecutar el OCR del documento.
    resultado_ocr = procesar_documento_ocr(
        ruta_archivo=ruta_pdf,
        idioma="spa+eng",
        dpi=300
    )

    assert resultado_ocr.total_paginas == 2

    assert resultado_ocr.paginas[0].metodo == "digital"
    assert resultado_ocr.paginas[1].metodo == "ocr_completo"

    # 7. Generar el documento Word.
    resultado_exportacion = exportar_ocr_a_word(
        resultado_ocr,
        ruta_word
    )

    # 8. Verificar que el Word exista.
    assert resultado_exportacion == str(ruta_word)
    assert ruta_word.is_file()
    assert ruta_word.stat().st_size > 0

    # 9. Abrir el documento Word real.
    documento_word = Document(str(ruta_word))

    # 10. Extraer los textos de sus parrafos.
    contenido = " ".join(
        parrafo.text
        for parrafo in documento_word.paragraphs
    )

    # Normalizar mayusculas y espacios.
    contenido = " ".join(
        contenido.upper().split()
    )

    # 11. Verificar texto digital.
    assert "DOCUMENTO DIGITAL DOCLAB" in contenido

    # 12. Verificar texto reconocido por OCR.
    assert "FACTURA" in contenido
    assert "DOCLAB" in contenido
    assert "2026" in contenido
