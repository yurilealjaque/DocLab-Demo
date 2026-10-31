
import pytest
import pymupdf

from doclab.document_engine.pdf_merger import unir_archivos_pdf
from doclab.document_engine.pdf_validator import (
    PDFCorruptoError,
    PDFProtegidoError,
)

import os
import hashlib
import doclab.document_engine.pdf_merger as pdf_merger
from pathlib import Path



def crear_pdf(ruta, textos):
    """Crea un PDF de prueba con una página por texto."""

    with pymupdf.open() as documento:
        for texto in textos:
            pagina = documento.new_page()
            pagina.insert_text((72, 72), texto)

        documento.save(str(ruta))


def test_unir_pdf_respeta_orden(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["Primera pagina", "Segunda pagina"])
    crear_pdf(origen_b, ["Tercera pagina"])

    resultado = unir_archivos_pdf(
        [origen_a, origen_b],
        destino
    )

    assert resultado == str(destino)

    with pymupdf.open(str(destino)) as documento:
        assert documento.page_count == 3

        textos = [
            pagina.get_text().strip()
            for pagina in documento
        ]

        assert textos == [
            "Primera pagina",
            "Segunda pagina",
            "Tercera pagina"
        ]


def test_rechaza_un_solo_pdf(tmp_path):
    origen = tmp_path / "a.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, ["Pagina uno"])

    with pytest.raises(ValueError):
        unir_archivos_pdf([origen], destino)

    assert not destino.exists()


def test_no_sobrescribe_destino(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])
    crear_pdf(origen_b, ["B"])
    crear_pdf(destino, ["Original"])

    with pytest.raises(FileExistsError):
        unir_archivos_pdf(
            [origen_a, origen_b],
            destino
        )

    with pymupdf.open(str(destino)) as documento:
        assert documento.page_count == 1
        assert documento[0].get_text().strip() == "Original"


def test_rechaza_archivo_inexistente(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "no_existe.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])

    with pytest.raises(FileNotFoundError):
        unir_archivos_pdf(
            [origen_a, origen_b],
            destino
        )

    assert not destino.exists()


def test_rechaza_pdf_corrupto(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "corrupto.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])
    origen_b.write_text(
        "Este archivo no es un PDF",
        encoding="utf-8"
    )

    with pytest.raises(PDFCorruptoError):
        unir_archivos_pdf(
            [origen_a, origen_b],
            destino
        )

    assert not destino.exists()

def test_rechaza_pdf_protegido(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "protegido.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["Documento A"])

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(
            str(origen_b),
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            user_pw="clave123",
            owner_pw="administrador456"
        )

    with pytest.raises(PDFProtegidoError):
        unir_archivos_pdf([origen_a, origen_b], destino)

    assert not destino.exists()


def test_limpia_temporal_si_falla_guardado(tmp_path, monkeypatch):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])
    crear_pdf(origen_b, ["B"])

    guardado_original = pymupdf.Document.save

    def guardar_con_error(documento, *args, **kwargs):
        raise RuntimeError("Fallo simulado de guardado")

    monkeypatch.setattr(
        pymupdf.Document,
        "save",
        guardar_con_error
    )

    with pytest.raises(RuntimeError, match="Fallo simulado"):
        unir_archivos_pdf([origen_a, origen_b], destino)

    assert not destino.exists()
    assert list(tmp_path.glob("doclab_union_*.pdf")) == []


def test_fallo_publicacion_limpia_temporal(tmp_path, monkeypatch):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])
    crear_pdf(origen_b, ["B"])

    def enlace_con_error(origen, destino):
        raise OSError("Fallo simulado de enlace")

    monkeypatch.setattr(pdf_merger.os, "link", enlace_con_error)

    with pytest.raises(OSError, match="No se pudo publicar"):
        unir_archivos_pdf([origen_a, origen_b], destino)

    assert not destino.exists()
    assert list(tmp_path.glob("doclab_union_*.pdf")) == []


def test_no_modifica_archivos_originales(tmp_path):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["Documento original A"])
    crear_pdf(origen_b, ["Documento original B"])

    def calcular_hash(ruta):
        return hashlib.sha256(ruta.read_bytes()).hexdigest()

    hash_a_antes = calcular_hash(origen_a)
    hash_b_antes = calcular_hash(origen_b)

    unir_archivos_pdf([origen_a, origen_b], destino)

    assert calcular_hash(origen_a) == hash_a_antes
    assert calcular_hash(origen_b) == hash_b_antes
    assert destino.exists()


def test_destino_creado_durante_publicacion(tmp_path, monkeypatch):
    origen_a = tmp_path / "a.pdf"
    origen_b = tmp_path / "b.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen_a, ["A"])
    crear_pdf(origen_b, ["B"])

    def simular_colision(temporal, ruta_destino):
        # Otro proceso crea el destino antes de publicar.
        Path(ruta_destino).write_bytes(b"archivo existente")
        raise FileExistsError("Destino ocupado")

    monkeypatch.setattr(
        pdf_merger.os,
        "link",
        simular_colision
    )

    with pytest.raises(FileExistsError):
        unir_archivos_pdf([origen_a, origen_b], destino)

    assert destino.read_bytes() == b"archivo existente"
    assert list(tmp_path.glob("doclab_union_*.pdf")) == []
