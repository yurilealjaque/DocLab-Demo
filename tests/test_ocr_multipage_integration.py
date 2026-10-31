
"""
Prueba de integracion real del OCR multipagina.

Comprueba:
- Extraccion directa de texto digital.
- OCR completo en imagen escaneada.
- OCR parcial en pagina con texto e imagen.
- Omision de una pagina vacia.
"""

import pymupdf

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.ocr_engine import (
    verificar_recursos_ocr
)


def crear_imagen_con_texto(texto):
    """
    Genera una imagen PNG con el texto indicado.

    Primero crea un PDF temporal en memoria
    y despues lo convierte a imagen.
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


def test_ocr_real_multipagina(tmp_path):

    # 1. Comprobar recursos OCR locales.
    verificar_recursos_ocr()

    ruta = tmp_path / "documento_multipagina.pdf"

    # 2. Generar imagenes con texto.
    imagen_escaneada = crear_imagen_con_texto(
        "FACTURA PRUEBA 2026"
    )

    imagen_incrustada = crear_imagen_con_texto(
        "CODIGO IMAGEN 5678"
    )

    # 3. Construir documento PDF.
    with pymupdf.open() as documento:

        # Pagina 1: solo texto digital.
        pagina_uno = documento.new_page(
            width=600,
            height=400
        )

        pagina_uno.insert_text(
            (50, 80),
            "CONTENIDO DIGITAL DOCLAB",
            fontsize=20
        )

        # Pagina 2: imagen de pagina completa.
        pagina_dos = documento.new_page(
            width=600,
            height=200
        )

        pagina_dos.insert_image(
            pagina_dos.rect,
            stream=imagen_escaneada
        )

        # Pagina 3: texto e imagen incrustada.
        pagina_tres = documento.new_page(
            width=600,
            height=500
        )

        pagina_tres.insert_text(
            (50, 50),
            "ENCABEZADO DIGITAL",
            fontsize=20
        )

        pagina_tres.insert_image(
            pymupdf.Rect(20, 130, 580, 320),
            stream=imagen_incrustada
        )

        # Pagina 4: pagina vacia.
        documento.new_page(
            width=600,
            height=400
        )

        documento.save(str(ruta))

    # 4. Ejecutar el procesamiento real.
    resultado = procesar_documento_ocr(
        ruta_archivo=ruta,
        idioma="spa+eng",
        dpi=300
    )

    # 5. Verificar estructura del documento.
    assert resultado.total_paginas == 4
    assert len(resultado.paginas) == 4

    metodos = tuple(
        pagina.metodo for pagina in resultado.paginas
    )

    assert metodos == (
        "digital",
        "ocr_completo",
        "ocr_parcial",
        "vacia"
    )

    # 6. Comprobar texto digital.
    texto_uno = " ".join(
        resultado.paginas[0].texto.upper().split()
    )

    assert "CONTENIDO DIGITAL" in texto_uno

    # 7. Comprobar OCR completo.
    texto_dos = " ".join(
        resultado.paginas[1].texto.upper().split()
    )

    assert "FACTURA" in texto_dos
    assert "PRUEBA" in texto_dos
    assert "2026" in texto_dos

    # 8. Comprobar OCR parcial.
    texto_tres = " ".join(
        resultado.paginas[2].texto.upper().split()
    )

    assert "ENCABEZADO DIGITAL" in texto_tres
    assert "CODIGO" in texto_tres
    assert "IMAGEN" in texto_tres
    assert "5678" in texto_tres

    # 9. Verificar pagina vacia.
    assert resultado.paginas[3].texto == ""
