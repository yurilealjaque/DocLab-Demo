
import pymupdf

import doclab.document_engine.ocr_document as modulo

from doclab.document_engine.ocr_document import (
    procesar_documento_ocr
)

from doclab.document_engine.ocr_engine import (
    ResultadoOCR,
    ErrorReconocimientoOCR
)


def crear_imagen():
    imagen = pymupdf.Pixmap(
        pymupdf.csRGB,
        pymupdf.IRect(0, 0, 100, 100),
        False
    )

    imagen.clear_with(180)
    return imagen


def test_documento_digital(tmp_path):
    ruta = tmp_path / "digital.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_text(
            (72, 72),
            "Hola desde DocLab"
        )
        documento.save(str(ruta))

    resultado = procesar_documento_ocr(ruta)

    assert resultado.total_paginas == 1
    assert resultado.paginas[0].metodo == "digital"
    assert "Hola desde DocLab" in resultado.paginas[0].texto


def test_documento_vacio(tmp_path):
    ruta = tmp_path / "vacio.pdf"

    with pymupdf.open() as documento:
        documento.new_page()
        documento.save(str(ruta))

    resultado = procesar_documento_ocr(ruta)

    assert resultado.paginas[0].metodo == "vacia"
    assert resultado.paginas[0].texto == ""


def test_documento_escaneado(monkeypatch, tmp_path):
    ruta = tmp_path / "escaneado.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_image(
            pagina.rect,
            pixmap=crear_imagen()
        )
        documento.save(str(ruta))

    llamadas = []

    def simular_ocr(**opciones):
        llamadas.append(opciones)

        return ResultadoOCR(
            numero_pagina=1,
            texto="Texto reconocido",
            idioma="spa+eng"
        )

    monkeypatch.setattr(
        modulo,
        "reconocer_texto_pagina",
        simular_ocr
    )

    resultado = procesar_documento_ocr(ruta)

    assert resultado.paginas[0].metodo == "ocr_completo"
    assert resultado.paginas[0].texto == "Texto reconocido"
    assert len(llamadas) == 1
    assert llamadas[0]["completo"] is True


def test_documento_texto_e_imagen(monkeypatch, tmp_path):
    ruta = tmp_path / "mixto.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()

        pagina.insert_text(
            (72, 72),
            "Texto digital"
        )

        pagina.insert_image(
            pymupdf.Rect(100, 100, 200, 200),
            pixmap=crear_imagen()
        )

        documento.save(str(ruta))

    llamadas = []

    def simular_ocr(**opciones):
        llamadas.append(opciones)

        return ResultadoOCR(
            numero_pagina=1,
            texto="Texto digital y reconocido",
            idioma="spa+eng"
        )

    monkeypatch.setattr(
        modulo,
        "reconocer_texto_pagina",
        simular_ocr
    )

    resultado = procesar_documento_ocr(ruta)

    assert resultado.paginas[0].metodo == "ocr_parcial"
    assert len(llamadas) == 1
    assert llamadas[0]["completo"] is False


def test_documento_multipagina(monkeypatch, tmp_path):
    ruta = tmp_path / "multipagina.pdf"

    with pymupdf.open() as documento:

        pagina_uno = documento.new_page()
        pagina_uno.insert_text(
            (72, 72),
            "Primera pagina"
        )

        pagina_dos = documento.new_page()
        pagina_dos.insert_image(
            pagina_dos.rect,
            pixmap=crear_imagen()
        )

        documento.new_page()

        documento.save(str(ruta))

    llamadas = []

    def simular_ocr(**opciones):
        llamadas.append(opciones)

        return ResultadoOCR(
            numero_pagina=opciones["numero_pagina"],
            texto="Texto del escaneo",
            idioma="spa+eng"
        )

    monkeypatch.setattr(
        modulo,
        "reconocer_texto_pagina",
        simular_ocr
    )

    resultado = procesar_documento_ocr(ruta)

    assert resultado.total_paginas == 3

    assert tuple(
        pagina.metodo for pagina in resultado.paginas
    ) == (
        "digital",
        "ocr_completo",
        "vacia"
    )

    assert len(llamadas) == 1
    assert llamadas[0]["numero_pagina"] == 2


def test_error_ocr_se_propaga(monkeypatch, tmp_path):
    import pytest

    ruta = tmp_path / "error.pdf"

    with pymupdf.open() as documento:
        pagina = documento.new_page()
        pagina.insert_image(
            pagina.rect,
            pixmap=crear_imagen()
        )
        documento.save(str(ruta))

    def simular_error(**opciones):
        raise ErrorReconocimientoOCR(
            "Error de reconocimiento"
        )

    monkeypatch.setattr(
        modulo,
        "reconocer_texto_pagina",
        simular_error
    )

    with pytest.raises(ErrorReconocimientoOCR):
        procesar_documento_ocr(ruta)
