
import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine import image_validator
from doclab.document_engine.image_validator import (
    validar_imagen,
    ImagenCorruptaError,
    ImagenDemasiadoGrandeError,
)


def crear_imagen(ruta, formato="PNG", ancho=100, alto=80):
    """Crea una imagen sintetica para las pruebas."""

    imagen = QImage(
        ancho,
        alto,
        QImage.Format.Format_RGB32,
    )
    imagen.fill(Qt.GlobalColor.white)

    assert imagen.save(str(ruta), formato)
    return ruta


def test_png_valido(tmp_path):
    ruta = crear_imagen(tmp_path / "foto.png")

    resultado = validar_imagen(ruta)

    assert resultado.formato == "png"
    assert resultado.ancho == 100
    assert resultado.alto == 80
    assert resultado.tamano_bytes > 0
    assert resultado.requiere_rotacion is False


def test_jpg_valido(tmp_path):
    ruta = crear_imagen(
        tmp_path / "foto.jpg",
        formato="JPEG",
    )

    resultado = validar_imagen(ruta)

    assert resultado.formato == "jpeg"
    assert resultado.ancho == 100
    assert resultado.alto == 80


def test_jpeg_valido(tmp_path):
    ruta = crear_imagen(
        tmp_path / "foto.jpeg",
        formato="JPEG",
    )

    resultado = validar_imagen(ruta)

    assert resultado.formato == "jpeg"


def test_archivo_inexistente(tmp_path):
    ruta = tmp_path / "inexistente.png"

    with pytest.raises(FileNotFoundError):
        validar_imagen(ruta)


def test_extension_no_permitida(tmp_path):
    ruta = tmp_path / "documento.txt"
    ruta.write_text("contenido de prueba", encoding="utf-8")

    with pytest.raises(ValueError):
        validar_imagen(ruta)


def test_archivo_vacio(tmp_path):
    ruta = tmp_path / "vacio.png"
    ruta.write_bytes(b"")

    with pytest.raises(ImagenCorruptaError):
        validar_imagen(ruta)


def test_imagen_falsa(tmp_path):
    ruta = tmp_path / "imagen.png"
    ruta.write_text("No soy una imagen", encoding="utf-8")

    with pytest.raises(ImagenCorruptaError):
        validar_imagen(ruta)


def test_extension_no_coincide_con_formato(tmp_path):
    ruta = crear_imagen(
        tmp_path / "foto.png",
        formato="JPEG",
    )

    with pytest.raises(ImagenCorruptaError):
        validar_imagen(ruta)


def test_imagen_supera_limite_de_bytes(
    tmp_path,
    monkeypatch,
):
    ruta = crear_imagen(tmp_path / "grande.png")

    monkeypatch.setattr(
        image_validator,
        "TAMANO_MAXIMO_MB",
        0,
    )

    with pytest.raises(ImagenDemasiadoGrandeError):
        validar_imagen(ruta)


def test_imagen_supera_limite_de_pixeles(
    tmp_path,
    monkeypatch,
):
    ruta = crear_imagen(
        tmp_path / "resolucion.png",
        ancho=100,
        alto=100,
    )

    monkeypatch.setattr(
        image_validator,
        "PIXELES_MAXIMOS",
        500,
    )

    with pytest.raises(ImagenDemasiadoGrandeError):
        validar_imagen(ruta)


def test_no_modifica_archivo_original(tmp_path):
    ruta = crear_imagen(tmp_path / "original.png")

    contenido_antes = ruta.read_bytes()

    validar_imagen(ruta)

    contenido_despues = ruta.read_bytes()

    assert contenido_antes == contenido_despues
