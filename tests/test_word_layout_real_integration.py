
"""
Integracion real del flujo de reconstruccion Word.

Verifica conjuntamente:
- Procesamiento OCR.
- Analisis de estructura PDF.
- Extraccion de imagenes.
- Plan de reconstruccion.
- Exportacion a Word.
"""

import pymupdf

from docx import Document

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr
)

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.pdf_layout import (
    analizar_estructura_pdf
)

from doclab.document_engine.pdf_image_extractor import (
    extraer_imagenes_pdf
)

from doclab.document_engine.word_layout_plan import (
    crear_plan_word
)

from doclab.document_engine.word_layout_export import (
    exportar_plan_a_word
)


def crear_imagen_con_texto(texto):
    """
    Construye una imagen PNG con palabras.

    Renderiza el texto en una imagen para
    que no exista una capa digital extraible.
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


def test_reconstruccion_word_real(tmp_path):

    # 1. Comprobar recursos OCR.
    verificar_recursos_ocr()

    ruta_pdf = tmp_path / "documento_original.pdf"
    ruta_word = tmp_path / "documento_reconstruido.docx"

    # 2. Preparar imagenes.
    imagen_mixta = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    # 3. Crear el PDF real.
    with pymupdf.open() as documento:

        # Pagina 1: texto digital.
        pagina_uno = documento.new_page(
            width=600,
            height=400
        )

        pagina_uno.insert_text(
            (50, 80),
            "DOCUMENTO DIGITAL DOCLAB",
            fontsize=20
        )

        # Pagina 2: contenido mixto.
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

        # Pagina 3: escaneo completo.
        pagina_tres = documento.new_page(
            width=600,
            height=200
        )

        pagina_tres.insert_image(
            pagina_tres.rect,
            stream=imagen_escaneada
        )

        # Pagina 4: vacia.
        documento.new_page(
            width=600,
            height=400
        )

        documento.save(str(ruta_pdf))

    # 4. Confirmar que el escaneo
    # no tiene texto digital.
    with pymupdf.open(str(ruta_pdf)) as documento:
        assert documento[2].get_text("text").strip() == ""

    # 5. Procesamiento OCR.
    resultado_ocr = procesar_documento_ocr(
        ruta_archivo=ruta_pdf,
        idioma="spa+eng",
        dpi=300
    )

    assert tuple(
        pagina.metodo
        for pagina in resultado_ocr.paginas
    ) == (
        "digital",
        "ocr_parcial",
        "ocr_completo",
        "vacia"
    )

    # 6. Analisis de estructura.
    resultado_estructura = analizar_estructura_pdf(
        ruta_pdf
    )

    # 7. Extraccion de imagenes.
    resultado_imagenes = extraer_imagenes_pdf(
        ruta_pdf
    )

    assert len(resultado_imagenes.imagenes) == 2

    # 8. Construir el plan de reconstruccion.
    resultado_plan = crear_plan_word(
        resultado_ocr,
        resultado_estructura
    )

    assert resultado_plan.total_paginas == 4

    # Solo se conserva la imagen de la pagina
    # mixta. La imagen del escaneo se omite.
    bloques_imagen = [
        elemento
        for elemento in resultado_plan.elementos
        if elemento.tipo == "imagen"
    ]

    assert len(bloques_imagen) == 1
    assert bloques_imagen[0].numero_pagina == 2

    # 9. Generar el Word.
    ruta_generada = exportar_plan_a_word(
        resultado_plan,
        resultado_imagenes,
        ruta_word
    )

    assert ruta_generada == str(ruta_word)
    assert ruta_word.is_file()

    # 10. Abrir el Word generado.
    documento_word = Document(str(ruta_word))

    # 11. Recuperar su texto editable.
    texto = " ".join(
        parrafo.text
        for parrafo in documento_word.paragraphs
    )

    texto = " ".join(
        texto.upper().split()
    )

    # Texto digital.
    assert "DOCUMENTO DIGITAL DOCLAB" in texto
    assert "ENCABEZADO DIGITAL" in texto

    # Texto OCR de la imagen incrustada.
    assert "CODIGO" in texto
    assert "IMAGEN" in texto
    assert "5678" in texto

    # Texto OCR del escaneo.
    assert "FACTURA" in texto
    assert "DOCLAB" in texto
    assert "2026" in texto

    # Evitar duplicar el texto digital mixto.
    assert texto.count("ENCABEZADO DIGITAL") == 1

    # 12. Comprobar imagen conservada.
    assert len(documento_word.inline_shapes) == 1

    # 13. Comprobar la secuencia de elementos.
    secuencia = []

    for parrafo in documento_word.paragraphs:

        if parrafo._p.xpath(".//w:drawing"):
            secuencia.append("IMAGEN")

        elif parrafo.text.strip():
            secuencia.append(
                parrafo.text.upper().strip()
            )

    posicion_encabezado = next(
        indice
        for indice, elemento in enumerate(secuencia)
        if "ENCABEZADO DIGITAL" in elemento
    )

    posicion_imagen = secuencia.index("IMAGEN")

    posicion_factura = next(
        indice
        for indice, elemento in enumerate(secuencia)
        if "FACTURA" in elemento
    )

    assert posicion_encabezado < posicion_imagen
    assert posicion_imagen < posicion_factura
