
import pymupdf

from docx import Document

from doclab.document_engine.pdf_to_word import (
    convertir_pdf_a_word
)


def test_conversion_real_pdf_a_word(tmp_path):
    # 1. Preparar las rutas de prueba.
    ruta_pdf = tmp_path / "documento.pdf"
    ruta_word = tmp_path / "documento.docx"

    texto_esperado = "Bienvenido a DocLab"

    # 2. Crear un PDF real.
    documento_pdf = pymupdf.open()
    pagina = documento_pdf.new_page()

    pagina.insert_text(
        (72, 72),
        texto_esperado
    )

    documento_pdf.save(str(ruta_pdf))
    documento_pdf.close()

    # 3. Ejecutar nuestro conversor.
    resultado = convertir_pdf_a_word(
        ruta_pdf,
        ruta_word
    )

    # 4. Comprobar que el archivo existe.
    assert ruta_word.exists()
    assert ruta_word.stat().st_size > 0
    assert resultado == str(ruta_word)

    # 5. Abrir el Word generado.
    documento_word = Document(str(ruta_word))

    # 6. Extraer el texto de sus parrafos.
    textos = []

    for parrafo in documento_word.paragraphs:
        textos.append(parrafo.text)

    contenido = " ".join(textos)

    # 7. Comprobar que el texto se conservo.
    assert texto_esperado in contenido
