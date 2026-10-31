
import pytest

import doclab.document_engine.ocr_engine as motor

from doclab.document_engine.ocr_engine import (
    ResultadoOCR,
    RecursosOCRNoDisponiblesError,
    ErrorReconocimientoOCR,
    verificar_recursos_ocr,
    reconocer_texto_pagina,
)


def crear_recursos_simulados(tmp_path):
    carpeta = tmp_path / "tessdata"
    carpeta.mkdir()

    (carpeta / "spa.traineddata").write_bytes(b"modelo_simulado")
    (carpeta / "eng.traineddata").write_bytes(b"modelo_simulado")

    return carpeta


def test_verificar_recursos_disponibles(tmp_path):
    carpeta = crear_recursos_simulados(tmp_path)

    resultado = verificar_recursos_ocr(
        carpeta_tessdata=carpeta
    )

    assert resultado == carpeta


def test_rechazar_idioma_faltante(tmp_path):
    carpeta = crear_recursos_simulados(tmp_path)

    with pytest.raises(RecursosOCRNoDisponiblesError):
        verificar_recursos_ocr(
            carpeta_tessdata=carpeta,
            idioma="fra"
        )


def test_rechazar_carpeta_inexistente(tmp_path):
    with pytest.raises(RecursosOCRNoDisponiblesError):
        verificar_recursos_ocr(
            carpeta_tessdata=tmp_path / "no_existe"
        )


def test_rechazar_pagina_invalida():
    with pytest.raises(ValueError):
        reconocer_texto_pagina("documento.pdf", 0)


def test_rechazar_pagina_fuera_de_rango(monkeypatch):
    monkeypatch.setattr(
        motor,
        "validar_pdf",
        lambda ruta: 2
    )

    with pytest.raises(ValueError):
        reconocer_texto_pagina("documento.pdf", 3)


def test_reconocimiento_simulado(tmp_path, monkeypatch):
    carpeta = crear_recursos_simulados(tmp_path)

    monkeypatch.setattr(
        motor,
        "validar_pdf",
        lambda ruta: 1
    )

    class PaginaSimulada:

        def get_textpage_ocr(self, **opciones):
            assert opciones["language"] == "spa+eng"
            assert opciones["tessdata"] == str(carpeta)
            return object()

        def get_text(self, formato, textpage):
            assert formato == "text"
            return "  Hola desde DocLab  "

    class DocumentoSimulado:

        def __enter__(self):
            return self

        def __exit__(self, tipo, valor, traza):
            pass

        def load_page(self, indice):
            assert indice == 0
            return PaginaSimulada()

    monkeypatch.setattr(
        motor.pymupdf,
        "open",
        lambda *args, **opciones: DocumentoSimulado()
    )

    resultado = reconocer_texto_pagina(
        "documento.pdf",
        numero_pagina=1,
        carpeta_tessdata=carpeta
    )

    assert resultado == ResultadoOCR(
        numero_pagina=1,
        texto="Hola desde DocLab",
        idioma="spa+eng"
    )


def test_error_interno_ocr(tmp_path, monkeypatch):
    carpeta = crear_recursos_simulados(tmp_path)

    monkeypatch.setattr(
        motor,
        "validar_pdf",
        lambda ruta: 1
    )

    def simular_error(*args, **opciones):
        raise RuntimeError("Error del motor OCR")

    monkeypatch.setattr(
        motor.pymupdf,
        "open",
        simular_error
    )

    with pytest.raises(ErrorReconocimientoOCR):
        reconocer_texto_pagina(
            "documento.pdf",
            numero_pagina=1,
            carpeta_tessdata=carpeta
        )
