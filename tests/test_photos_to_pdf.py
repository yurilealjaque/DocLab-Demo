
import os

import pymupdf
import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine.photo_manager import GestorFotografias
from doclab.document_engine.photos_to_pdf import (
    generar_pdf_fotografias,
    ErrorFotosPDF,
)


def crear_foto(ruta, ancho=120, alto=80, formato="PNG"):
    """Genera una imagen sintetica para las pruebas."""
    imagen = QImage(
        ancho,
        alto,
        QImage.Format.Format_RGB32,
    )
    imagen.fill(Qt.GlobalColor.white)

    assert imagen.save(str(ruta), formato)
    return ruta


def preparar_gestor(tmp_path, cantidad=3):
    """Prepara un gestor con fotografias validas."""
    gestor = GestorFotografias()
    rutas = []

    for numero in range(cantidad):
        ruta = crear_foto(
            tmp_path / f"foto_{numero}.png",
            ancho=120 + numero * 20,
            alto=80,
        )
        rutas.append(ruta)

    gestor.agregar_fotografias(rutas)
    return gestor, rutas


def test_generar_pdf_una_fotografia(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, cantidad=1)
    destino = tmp_path / "resultado.pdf"

    resultado = generar_pdf_fotografias(gestor, destino)

    assert destino.is_file()
    assert resultado.numero_paginas == 1
    assert resultado.ruta_destino == destino
    assert resultado.tamano_bytes > 0


def test_generar_pdf_multipagina(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, cantidad=3)
    destino = tmp_path / "clases.pdf"

    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(destino) as documento:
        assert documento.page_count == 3


def test_paginas_contienen_imagenes(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, cantidad=3)
    destino = tmp_path / "imagenes.pdf"

    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(destino) as documento:
        for pagina in documento:
            assert len(pagina.get_images(full=True)) >= 1


def test_conservar_orden_de_fotografias(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, cantidad=3)

    # Mover la tercera fotografia a la primera posicion.
    gestor.subir_fotografia(2)
    gestor.subir_fotografia(1)

    destino = tmp_path / "ordenado.pdf"
    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(destino) as documento:
        anchos = [
            round(pagina.rect.width)
            for pagina in documento
        ]

    # Foto 3: 160 px; foto 1: 120 px; foto 2: 140 px.
    assert anchos == [160, 120, 140]


def test_conservar_proporciones(tmp_path):
    gestor = GestorFotografias()

    ruta = crear_foto(
        tmp_path / "horizontal.png",
        ancho=200,
        alto=100,
    )
    gestor.agregar_fotografia(ruta)

    destino = tmp_path / "proporciones.pdf"
    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(destino) as documento:
        pagina = documento[0]
        assert pagina.rect.width == 200
        assert pagina.rect.height == 100


def test_aceptar_jpeg(tmp_path):
    gestor = GestorFotografias()

    ruta = crear_foto(
        tmp_path / "foto.jpg",
        formato="JPEG",
    )
    gestor.agregar_fotografia(ruta)

    destino = tmp_path / "jpeg.pdf"
    generar_pdf_fotografias(gestor, destino)

    with pymupdf.open(destino) as documento:
        assert documento.page_count == 1


def test_rechazar_gestor_vacio(tmp_path):
    gestor = GestorFotografias()

    with pytest.raises(ValueError):
        generar_pdf_fotografias(
            gestor,
            tmp_path / "vacio.pdf",
        )


def test_rechazar_extension_incorrecta(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, cantidad=1)

    with pytest.raises(ValueError):
        generar_pdf_fotografias(
            gestor,
            tmp_path / "resultado.txt",
        )


def test_no_sobrescribir_destino(tmp_path):
    gestor, _ = preparar_gestor(tmp_path, cantidad=1)
    destino = tmp_path / "existente.pdf"

    destino.write_bytes(b"contenido anterior")

    with pytest.raises(FileExistsError):
        generar_pdf_fotografias(gestor, destino)

    assert destino.read_bytes() == b"contenido anterior"


def test_no_modificar_fotografias(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, cantidad=3)

    contenidos_antes = [
        ruta.read_bytes()
        for ruta in rutas
    ]

    generar_pdf_fotografias(
        gestor,
        tmp_path / "resultado.pdf",
    )

    contenidos_despues = [
        ruta.read_bytes()
        for ruta in rutas
    ]

    assert contenidos_antes == contenidos_despues


def test_archivo_eliminado_antes_de_convertir(tmp_path):
    gestor, rutas = preparar_gestor(tmp_path, cantidad=1)
    rutas[0].unlink()

    destino = tmp_path / "resultado.pdf"

    with pytest.raises(FileNotFoundError):
        generar_pdf_fotografias(gestor, destino)

    assert not destino.exists()


def test_limpiar_temporal_si_falla_publicacion(
    tmp_path,
    monkeypatch,
):
    gestor, _ = preparar_gestor(tmp_path, cantidad=1)
    destino = tmp_path / "resultado.pdf"

    def simular_error(origen, destino_final):
        raise OSError("Fallo simulado al publicar")

    monkeypatch.setattr(os, "link", simular_error)

    with pytest.raises(OSError):
        generar_pdf_fotografias(gestor, destino)

    temporales = list(tmp_path.glob(".doclab_fotos_*.pdf"))

    assert temporales == []
    assert not destino.exists()


def test_rechazar_tipo_incorrecto(tmp_path):
    with pytest.raises(TypeError):
        generar_pdf_fotografias(
            ["foto.png"],
            tmp_path / "resultado.pdf",
        )
