
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

import zipfile

import doclab.document_engine.pdf_to_word as motor


def crear_conversor_simulado():
    """
    Genera una clase que simula una conversion
    y produce un DOCX estructuralmente valido.
    """

    class ConversorSimulado:

        def __init__(self, origen):
            self.origen = origen

        def convert(self, destino):
            with zipfile.ZipFile(
                destino, "w"
            ) as documento:
                documento.writestr(
                    "[Content_Types].xml",
                    "<Types/>"
                )
                documento.writestr(
                    "word/document.xml",
                    "<document/>"
                )

        def close(self):
            pass

    return ConversorSimulado


def test_publicacion_segura(tmp_path, monkeypatch):
    origen = tmp_path / "entrada.pdf"
    destino = tmp_path / "salida.docx"

    origen.write_bytes(b"PDF simulado")

    monkeypatch.setattr(
        motor,
        "Converter",
        crear_conversor_simulado()
    )

    resultado = motor.convertir_pdf_a_word(
        origen, destino
    )

    assert resultado == str(destino)
    assert destino.is_file()
    assert zipfile.is_zipfile(destino)
    assert list(tmp_path.glob("doclab_*.docx")) == []


def test_word_corrupto_no_se_publica(
    tmp_path, monkeypatch
):
    origen = tmp_path / "entrada.pdf"
    destino = tmp_path / "salida.docx"

    origen.write_bytes(b"PDF simulado")

    class ConversorCorrupto:

        def __init__(self, origen):
            pass

        def convert(self, destino):
            with open(destino, "wb") as archivo:
                archivo.write(b"Contenido no valido")

        def close(self):
            pass

    monkeypatch.setattr(
        motor, "Converter", ConversorCorrupto
    )

    with pytest.raises(ValueError):
        motor.convertir_pdf_a_word(
            origen, destino
        )

    assert not destino.exists()
    assert list(tmp_path.glob("doclab_*.docx")) == []


def test_destino_creado_durante_conversion(
    tmp_path, monkeypatch
):
    origen = tmp_path / "entrada.pdf"
    destino = tmp_path / "salida.docx"

    origen.write_bytes(b"PDF simulado")

    monkeypatch.setattr(
        motor,
        "Converter",
        crear_conversor_simulado()
    )

    def simular_publicacion(temporal, destino_final):
        # Otro proceso crea el archivo
        # antes de que DocLab pueda publicarlo.
        with open(destino_final, "xb") as archivo:
            archivo.write(b"Archivo ajeno")

        raise FileExistsError(
            "El destino ya existe"
        )

    monkeypatch.setattr(
        motor.os, "link", simular_publicacion
    )

    with pytest.raises(FileExistsError):
        motor.convertir_pdf_a_word(
            origen, destino
        )

    # El documento ajeno no debe modificarse.
    assert destino.read_bytes() == b"Archivo ajeno"

    # Los temporales propios deben limpiarse.
    assert list(tmp_path.glob("doclab_*.docx")) == []
