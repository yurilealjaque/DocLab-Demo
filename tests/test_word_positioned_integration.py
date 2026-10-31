
"""
Prueba de integracion real del plan OCR posicionado.

Comprueba el flujo:

PDF -> OCR -> Coordenadas -> Plan -> Word

No utiliza simulaciones del reconocimiento OCR.
"""

import pymupdf

from docx import Document

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr
)

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.ocr_text_blocks import (
    extraer_texto_posicionado
)

from doclab.document_engine.pdf_layout import (
    analizar_estructura_pdf
)

from doclab.document_engine.pdf_image_extractor import (
    extraer_imagenes_pdf
)

from doclab.document_engine.word_positioned_plan import (
    crear_plan_word_posicionado
)

from doclab.document_engine.word_layout_export import (
    exportar_plan_a_word
)


def crear_imagen_con_texto(texto):
    """
    Genera una imagen PNG con texto visible.
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


def test_integracion_ocr_posicionado_a_word(tmp_path):

    # 1. Verificar los modelos OCR locales.
    verificar_recursos_ocr()

    ruta_pdf = tmp_path / "original.pdf"
    ruta_word = tmp_path / "posicionado.docx"

    imagen_mixta = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA DOCLAB 2026"
    )

    # 2. Construir el PDF de prueba.
    with pymupdf.open() as documento:

        # Pagina 1: texto digital e imagen.
        pagina_uno = documento.new_page(
            width=600,
            height=500
        )

        pagina_uno.insert_text(
            (50, 60),
            "ENCABEZADO DIGITAL",
            fontsize=20
        )

        pagina_uno.insert_image(
            pymupdf.Rect(20, 130, 580, 320),
            stream=imagen_mixta
        )

        # Pagina 2: escaneo completo.
        pagina_dos = documento.new_page(
            width=600,
            height=200
        )

        pagina_dos.insert_image(
            pagina_dos.rect,
            stream=imagen_escaneada
        )

        documento.save(str(ruta_pdf))

    # 3. Procesar el contenido del documento.
    resultado_ocr = procesar_documento_ocr(
        ruta_archivo=ruta_pdf,
        idioma="spa+eng",
        dpi=300
    )

    assert tuple(
        pagina.metodo
        for pagina in resultado_ocr.paginas
    ) == (
        "ocr_parcial",
        "ocr_completo"
    )

    # 4. Recuperar los fragmentos con coordenadas.
    resultados_posicionados = []

    for pagina in resultado_ocr.paginas:

        if pagina.metodo not in (
            "ocr_parcial",
            "ocr_completo"
        ):
            continue

        resultado = extraer_texto_posicionado(
            ruta_archivo=ruta_pdf,
            numero_pagina=pagina.numero_pagina,
            idioma="spa+eng",
            dpi=300,
            completo=(
                pagina.metodo == "ocr_completo"
            )
        )

        resultados_posicionados.append(resultado)

    # 5. Obtener la estructura y las imagenes.
    resultado_estructura = analizar_estructura_pdf(
        ruta_pdf
    )

    resultado_imagenes = extraer_imagenes_pdf(
        ruta_pdf
    )

    # 6. Crear el plan con coordenadas OCR.
    plan = crear_plan_word_posicionado(
        resultado_ocr,
        resultado_estructura,
        tuple(resultados_posicionados)
    )

    assert plan.total_paginas == 2

    # 7. Verificar texto e imagenes del plan.
    textos_plan = [
        elemento.texto
        for elemento in plan.elementos
        if elemento.tipo == "texto"
    ]

    texto_plan = " ".join(
        " ".join(textos_plan).upper().split()
    )

    assert "ENCABEZADO DIGITAL" in texto_plan
    assert "CODIGO" in texto_plan
    assert "IMAGEN" in texto_plan
    assert "5678" in texto_plan
    assert "FACTURA" in texto_plan

    assert texto_plan.count(
        "ENCABEZADO DIGITAL"
    ) == 1

    imagenes_plan = [
        elemento
        for elemento in plan.elementos
        if elemento.tipo == "imagen"
    ]

    # Conservamos la imagen mixta, pero no
    # repetimos la pagina escaneada completa.
    assert len(imagenes_plan) == 1
    assert imagenes_plan[0].numero_pagina == 1

    # 8. Exportar el plan a un Word real.
    exportar_plan_a_word(
        resultado_plan=plan,
        resultado_imagenes=resultado_imagenes,
        ruta_destino=ruta_word
    )

    assert ruta_word.is_file()

    # 9. Comprobar el contenido del Word.
    documento_word = Document(str(ruta_word))

    texto_word = " ".join(
        parrafo.text
        for parrafo in documento_word.paragraphs
    )

    texto_word = " ".join(
        texto_word.upper().split()
    )

    assert "ENCABEZADO DIGITAL" in texto_word
    assert "CODIGO" in texto_word
    assert "IMAGEN" in texto_word
    assert "5678" in texto_word
    assert "FACTURA" in texto_word
    assert "DOCLAB" in texto_word
    assert "2026" in texto_word

    assert texto_word.count(
        "ENCABEZADO DIGITAL"
    ) == 1

    # La imagen mixta se conserva.
    assert len(documento_word.inline_shapes) == 1
