
import pytest

from doclab.document_engine.pdf_to_word import (
    convertir_pdf_a_word
)


def test_pdf_inexistente(tmp_path):
    origen = tmp_path / "inexistente.pdf"
    destino = tmp_path / "resultado.docx"

    with pytest.raises(FileNotFoundError):
        convertir_pdf_a_word(origen, destino)


def test_extension_origen_incorrecta(tmp_path):
    origen = tmp_path / "documento.txt"
    destino = tmp_path / "resultado.docx"

    origen.write_text("Documento de prueba")

    with pytest.raises(ValueError):
        convertir_pdf_a_word(origen, destino)


def test_extension_destino_incorrecta(tmp_path):
    origen = tmp_path / "documento.pdf"
    destino = tmp_path / "resultado.txt"

    origen.write_bytes(b"PDF de prueba")

    with pytest.raises(ValueError):
        convertir_pdf_a_word(origen, destino)


def test_no_sobrescribir_documento(tmp_path):
    origen = tmp_path / "documento.pdf"
    destino = tmp_path / "resultado.docx"

    origen.write_bytes(b"PDF de prueba")
    destino.write_bytes(b"Contenido original")

    with pytest.raises(FileExistsError):
        convertir_pdf_a_word(origen, destino)

    assert destino.read_bytes() == b"Contenido original"


def test_carpeta_destino_inexistente(tmp_path):
    origen = tmp_path / "documento.pdf"
    destino = tmp_path / "otra_carpeta" / "resultado.docx"

    origen.write_bytes(b"PDF de prueba")

    with pytest.raises(FileNotFoundError):
        convertir_pdf_a_word(origen, destino)
