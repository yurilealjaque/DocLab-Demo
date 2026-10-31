
import pytest
import pymupdf

from doclab.document_engine.pdf_splitter import (
    extraer_rango_pdf
)
import hashlib

import doclab.document_engine.pdf_splitter as modulo_division

from doclab.document_engine.pdf_validator import (
    PDFProtegidoError,
    PDFCorruptoError,
)
from doclab.document_engine.pdf_splitter import (
    extraer_rango_pdf,
    extraer_paginas_pdf,
)

from doclab.document_engine.pdf_splitter import (
    extraer_rango_pdf,
    extraer_paginas_pdf,
    separar_paginas_pdf,
)



def crear_pdf(ruta, cantidad_paginas):
    """
    Crea un PDF con paginas identificables.
    """

    with pymupdf.open() as documento:
        for numero in range(1, cantidad_paginas + 1):
            pagina = documento.new_page()

            pagina.insert_text(
                (72, 72),
                f"Pagina {numero}"
            )

        documento.save(str(ruta))


def test_extraer_rango_correcto(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "extraido.pdf"

    crear_pdf(origen, 10)

    resultado = extraer_rango_pdf(
        origen,
        destino,
        3,
        7
    )

    assert resultado == str(destino)

    with pymupdf.open(str(destino)) as documento:
        assert documento.page_count == 5

        textos = [
            pagina.get_text().strip()
            for pagina in documento
        ]

        assert textos == [
            "Pagina 3",
            "Pagina 4",
            "Pagina 5",
            "Pagina 6",
            "Pagina 7"
        ]


def test_rechazar_rango_invalido(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "extraido.pdf"

    crear_pdf(origen, 5)

    with pytest.raises(ValueError):
        extraer_rango_pdf(
            origen,
            destino,
            4,
            8
        )

    assert not destino.exists()


def test_no_sobrescribir_destino(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "extraido.pdf"

    crear_pdf(origen, 5)
    crear_pdf(destino, 2)

    with pytest.raises(FileExistsError):
        extraer_rango_pdf(
            origen,
            destino,
            1,
            3
        )

    with pymupdf.open(str(destino)) as documento:
        assert documento.page_count == 2

def test_rechaza_pdf_protegido(tmp_path):
    """
    Comprueba que no se puedan extraer paginas
    de un PDF que requiere contrasena.
    """

    origen = tmp_path / "protegido.pdf"
    destino = tmp_path / "resultado.pdf"

    with pymupdf.open() as documento:
        documento.new_page()

        documento.save(
            str(origen),
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            user_pw="clave123",
            owner_pw="administrador456"
        )

    with pytest.raises(PDFProtegidoError):
        extraer_rango_pdf(origen, destino, 1, 1)

    assert not destino.exists()


def test_rechaza_pdf_corrupto(tmp_path):
    """
    Comprueba que un archivo falso con extension
    PDF sea rechazado.
    """

    origen = tmp_path / "corrupto.pdf"
    destino = tmp_path / "resultado.pdf"

    origen.write_text(
        "Este contenido no es un PDF",
        encoding="utf-8"
    )

    with pytest.raises(PDFCorruptoError):
        extraer_rango_pdf(origen, destino, 1, 2)

    assert not destino.exists()


def test_rechaza_numeracion_invalida(tmp_path):
    """
    Comprueba que se rechacen paginas anteriores
    a la primera y rangos invertidos.
    """

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, 5)

    rangos_invalidos = [
        (0, 3),
        (-1, 3),
        (4, 2),
        (1.5, 3),
    ]

    for inicio, fin in rangos_invalidos:
        with pytest.raises(ValueError):
            extraer_rango_pdf(
                origen,
                destino,
                inicio,
                fin
            )

    assert not destino.exists()


def test_no_modifica_pdf_original(tmp_path):
    """
    Comprueba la integridad binaria del documento
    original mediante SHA-256.
    """

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "extraido.pdf"

    crear_pdf(origen, 5)

    hash_antes = hashlib.sha256(
        origen.read_bytes()
    ).hexdigest()

    extraer_rango_pdf(
        origen,
        destino,
        2,
        4
    )

    hash_despues = hashlib.sha256(
        origen.read_bytes()
    ).hexdigest()

    assert hash_antes == hash_despues
    assert destino.exists()


def test_fallo_publicacion_limpia_temporal(
    tmp_path,
    monkeypatch
):
    """
    Simula un error al publicar el documento
    y comprueba que se elimine el temporal.
    """

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, 5)

    def enlace_con_error(temporal, destino_final):
        raise OSError(
            "Fallo simulado de publicacion"
        )

    monkeypatch.setattr(
        modulo_division.os,
        "link",
        enlace_con_error
    )

    with pytest.raises(
        OSError,
        match="No fue posible publicar"
    ):
        extraer_rango_pdf(
            origen,
            destino,
            2,
            4
        )

    assert not destino.exists()

    temporales = list(
        tmp_path.glob("doclab_division_*.pdf")
    )

    assert temporales == []

def test_extraer_paginas_especificas(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "seleccion.pdf"

    crear_pdf(origen, 10)

    resultado = extraer_paginas_pdf(
        origen,
        destino,
        [1, 4, 8]
    )

    assert resultado == str(destino)

    with pymupdf.open(str(destino)) as documento:
        assert documento.page_count == 3

        textos = [
            pagina.get_text().strip()
            for pagina in documento
        ]

        assert textos == [
            "Pagina 1",
            "Pagina 4",
            "Pagina 8"
        ]


def test_respeta_orden_personalizado(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "ordenado.pdf"

    crear_pdf(origen, 10)

    extraer_paginas_pdf(
        origen,
        destino,
        [8, 1, 4]
    )

    with pymupdf.open(str(destino)) as documento:
        textos = [
            pagina.get_text().strip()
            for pagina in documento
        ]

        assert textos == [
            "Pagina 8",
            "Pagina 1",
            "Pagina 4"
        ]


def test_rechaza_paginas_fuera_de_rango(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, 5)

    with pytest.raises(ValueError):
        extraer_paginas_pdf(
            origen,
            destino,
            [1, 3, 9]
        )

    assert not destino.exists()


def test_rechaza_paginas_duplicadas(tmp_path):
    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, 5)

    with pytest.raises(ValueError):
        extraer_paginas_pdf(
            origen,
            destino,
            [1, 3, 3]
        )

    assert not destino.exists()


def test_separar_todas_las_paginas(tmp_path):
    origen = tmp_path / "original.pdf"
    carpeta_salida = tmp_path / "salida"
    carpeta_salida.mkdir()

    crear_pdf(origen, 4)

    resultados = separar_paginas_pdf(
        origen,
        carpeta_salida
    )

    assert len(resultados) == 4

    for numero, ruta in enumerate(resultados, start=1):
        with pymupdf.open(ruta) as documento:
            assert documento.page_count == 1
            assert documento[0].get_text().strip() == (
                f"Pagina {numero}"
            )


def test_separacion_no_sobrescribe_archivos(tmp_path):
    origen = tmp_path / "original.pdf"
    carpeta_salida = tmp_path / "salida"
    carpeta_salida.mkdir()

    crear_pdf(origen, 3)

    archivo_existente = (
        carpeta_salida / "original_pagina_002.pdf"
    )
    crear_pdf(archivo_existente, 1)

    contenido_original = archivo_existente.read_bytes()

    with pytest.raises(FileExistsError):
        separar_paginas_pdf(
            origen,
            carpeta_salida
        )

    assert archivo_existente.read_bytes() == (
        contenido_original
    )

    assert len(list(carpeta_salida.glob("*.pdf"))) == 1


def test_separacion_limpia_si_falla_publicacion(
    tmp_path,
    monkeypatch
):
    origen = tmp_path / "original.pdf"
    carpeta_salida = tmp_path / "salida"
    carpeta_salida.mkdir()

    crear_pdf(origen, 3)

    enlace_original = modulo_division.os.link
    llamadas = []

    def enlace_con_fallo(temporal, destino):
        llamadas.append(destino)

        if len(llamadas) == 2:
            raise OSError(
                "Fallo simulado en segunda publicacion"
            )

        return enlace_original(temporal, destino)

    monkeypatch.setattr(
        modulo_division.os,
        "link",
        enlace_con_fallo
    )

    with pytest.raises(
        OSError,
        match="Fallo simulado"
    ):
        separar_paginas_pdf(
            origen,
            carpeta_salida
        )

    # No deben quedar resultados parciales.
    assert list(carpeta_salida.iterdir()) == []

    
def test_no_sobrescribe_archivo_creado_durante_extraccion(
    tmp_path,
    monkeypatch
):
    """
    Simula que otro programa crea el destino
    justo antes de publicar el PDF extraido.

    Comprueba que DocLab no lo sobrescriba.
    """

    origen = tmp_path / "original.pdf"
    destino = tmp_path / "resultado.pdf"

    crear_pdf(origen, 5)

    contenido_externo = b"Archivo creado por otro programa"

    def simular_colision(temporal, ruta_destino):
        # Otro programa crea el archivo antes
        # de que DocLab pueda publicarlo.
        ruta_destino.write_bytes(contenido_externo)

        raise FileExistsError(
            "El archivo ya existe."
        )

    monkeypatch.setattr(
        modulo_division.os,
        "link",
        simular_colision
    )

    with pytest.raises(FileExistsError):
        extraer_rango_pdf(
            origen,
            destino,
            2,
            4
        )

    # El archivo externo debe permanecer intacto.
    assert destino.read_bytes() == contenido_externo

    # No deben quedar temporales.
    assert list(
        tmp_path.glob("doclab_division_*.pdf")
    ) == []


def test_separacion_con_colision_conserva_archivo_externo(
    tmp_path,
    monkeypatch
):
    """
    Simula que aparece un archivo externo
    durante la publicacion de varias paginas.

    Comprueba que:
    - Se retiran las salidas parciales de DocLab.
    - No se elimina el archivo externo.
    - El PDF original permanece intacto.
    """

    origen = tmp_path / "original.pdf"

    carpeta_salida = tmp_path / "salida"
    carpeta_salida.mkdir()

    crear_pdf(origen, 3)

    contenido_original = origen.read_bytes()
    contenido_externo = b"Documento externo protegido"

    enlace_original = modulo_division.os.link
    llamadas = 0

    def simular_colision(temporal, destino):
        nonlocal llamadas

        llamadas += 1

        if llamadas == 2:
            # Otro programa crea el segundo archivo
            # antes de su publicacion.
            destino.write_bytes(contenido_externo)

            raise FileExistsError(
                "Archivo creado por otro programa."
            )

        return enlace_original(temporal, destino)

    monkeypatch.setattr(
        modulo_division.os,
        "link",
        simular_colision
    )

    with pytest.raises(FileExistsError):
        separar_paginas_pdf(
            origen,
            carpeta_salida
        )

    archivo_externo = (
        carpeta_salida / "original_pagina_002.pdf"
    )

    # Debe conservarse el archivo externo.
    assert archivo_externo.read_bytes() == (
        contenido_externo
    )

    # Debe retirarse la primera pagina
    # que DocLab alcanzo a publicar.
    assert not (
        carpeta_salida / "original_pagina_001.pdf"
    ).exists()

    # No debe generarse la tercera pagina.
    assert not (
        carpeta_salida / "original_pagina_003.pdf"
    ).exists()

    # El archivo original no debe cambiar.
    assert origen.read_bytes() == contenido_original

    # La carpeta temporal debe haberse eliminado.
    assert list(
        carpeta_salida.glob("doclab_division_*")
    ) == []

