
"""
Pruebas del motor de compresión PDF.
"""

import hashlib

import pymupdf
import pytest

from doclab.document_engine.pdf_compressor import (
    comprimir_pdf,
    SinReduccionError,
    ResultadoCompresion,
    detectar_firmas,
)


def crear_pdf_prueba(ruta, paginas=1):
    """Genera un PDF con contenido sin comprimir."""

    with pymupdf.open() as documento:
        for numero in range(paginas):
            pagina = documento.new_page()

            for indice in range(60):
                pagina.insert_text(
                    (50, 50 + indice * 10),
                    f"Contenido de prueba {numero} "
                    f"- texto repetido numero {indice}"
                )

        documento.save(
            str(ruta),
            deflate=False,
            use_objstms=0
        )


def calcular_hash(ruta):
    return hashlib.sha256(
        ruta.read_bytes()
    ).hexdigest()


def test_compresion_reduce_tamano(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "comprimido.pdf"

    crear_pdf_prueba(origen)

    resultado = comprimir_pdf(origen, destino)

    assert isinstance(
        resultado,
        ResultadoCompresion
    )
    assert destino.is_file()
    assert resultado.tamano_final < resultado.tamano_original
    assert resultado.bytes_ahorrados > 0
    assert resultado.porcentaje_reduccion > 0


def test_compresion_conserva_paginas_y_texto(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "comprimido.pdf"

    crear_pdf_prueba(origen, paginas=2)

    comprimir_pdf(origen, destino)

    with pymupdf.open(str(origen)) as original:
        with pymupdf.open(str(destino)) as final:
            assert final.page_count == original.page_count

            for indice in range(original.page_count):
                assert (
                    original[indice].get_text()
                    == final[indice].get_text()
                )


def test_no_modifica_original(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "comprimido.pdf"

    crear_pdf_prueba(origen)

    hash_inicial = calcular_hash(origen)

    comprimir_pdf(origen, destino)

    assert calcular_hash(origen) == hash_inicial


def test_rechaza_archivo_inexistente(tmp_path):
    origen = tmp_path / "inexistente.pdf"
    destino = tmp_path / "salida.pdf"

    with pytest.raises(FileNotFoundError):
        comprimir_pdf(origen, destino)

    assert not destino.exists()


def test_rechaza_destino_existente(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "existente.pdf"

    crear_pdf_prueba(origen)
    crear_pdf_prueba(destino)

    hash_inicial = calcular_hash(destino)

    with pytest.raises(FileExistsError):
        comprimir_pdf(origen, destino)

    assert calcular_hash(destino) == hash_inicial


def test_rechaza_destino_igual_origen(tmp_path):
    origen = tmp_path / "original.pdf"

    crear_pdf_prueba(origen)

    with pytest.raises(ValueError):
        comprimir_pdf(origen, origen)


def test_rechaza_extension_incorrecta(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "salida.txt"

    crear_pdf_prueba(origen)

    with pytest.raises(ValueError):
        comprimir_pdf(origen, destino)


def test_rechaza_pdf_corrupto(tmp_path):
    origen = tmp_path / "corrupto.pdf"
    destino = tmp_path / "salida.pdf"

    origen.write_text(
        "Este archivo no es un PDF",
        encoding="utf-8"
    )

    with pytest.raises(Exception):
        comprimir_pdf(origen, destino)

    assert not destino.exists()


def test_detectar_firmas_documento_simple(tmp_path):
    origen = tmp_path / "original.pdf"

    crear_pdf_prueba(origen)

    with pymupdf.open(str(origen)) as documento:
        assert detectar_firmas(documento) is False


def test_sin_ahorro_no_publica(tmp_path, monkeypatch):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "comprimido.pdf"

    crear_pdf_prueba(origen)

    import doclab.document_engine.pdf_compressor as modulo

    tamano_real = modulo.Path.stat

    def simular_tamano(ruta, *args, **kwargs):
        resultado = tamano_real(ruta, *args, **kwargs)

        if ruta.name.startswith("doclab_compresion_"):
            class TamanoSimulado:
                st_size = origen.stat().st_size

            return TamanoSimulado()

        return resultado

    monkeypatch.setattr(
        modulo.Path,
        "stat",
        simular_tamano
    )

    with pytest.raises(SinReduccionError):
        comprimir_pdf(origen, destino)

    assert not destino.exists()
    assert list(
        tmp_path.glob("doclab_compresion_*.pdf")
    ) == []


def test_limpia_temporal_si_falla_guardado(
    tmp_path,
    monkeypatch
):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "salida.pdf"

    crear_pdf_prueba(origen)

    def guardar_con_error(documento, *args, **kwargs):
        raise RuntimeError("Fallo simulado de guardado")

    monkeypatch.setattr(
        pymupdf.Document,
        "save",
        guardar_con_error
    )

    with pytest.raises(
        RuntimeError,
        match="Fallo simulado"
    ):
        comprimir_pdf(origen, destino)

    assert not destino.exists()
    assert list(
        tmp_path.glob("doclab_compresion_*.pdf")
    ) == []


def test_no_sobrescribe_destino_en_colision(
    tmp_path,
    monkeypatch
):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "salida.pdf"

    crear_pdf_prueba(origen)

    import doclab.document_engine.pdf_compressor as modulo

    def simular_colision(temporal, ruta_destino):
        ruta_destino = modulo.Path(ruta_destino)
        ruta_destino.write_bytes(b"archivo de otro proceso")
        raise FileExistsError("Colision simulada")

    monkeypatch.setattr(
        modulo.os,
        "link",
        simular_colision
    )

    with pytest.raises(FileExistsError):
        comprimir_pdf(origen, destino)

    assert destino.read_bytes() == b"archivo de otro proceso"

    assert list(
        tmp_path.glob("doclab_compresion_*.pdf")
    ) == []
