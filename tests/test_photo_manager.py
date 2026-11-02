
import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from doclab.document_engine.photo_manager import (
    GestorFotografias,
    FotografiaDuplicadaError,
    FotografiaNoEncontradaError,
)


def crear_fotografia(ruta):
    """Crea una fotografia PNG para pruebas."""
    imagen = QImage(
        100,
        80,
        QImage.Format.Format_RGB32,
    )
    imagen.fill(Qt.GlobalColor.white)

    assert imagen.save(str(ruta), "PNG")
    return ruta


def preparar_tres_fotografias(tmp_path):
    """Crea tres fotografias con nombres diferentes."""
    return [
        crear_fotografia(tmp_path / "foto_1.png"),
        crear_fotografia(tmp_path / "foto_2.png"),
        crear_fotografia(tmp_path / "foto_3.png"),
    ]


def test_gestor_inicialmente_vacio():
    gestor = GestorFotografias()

    assert gestor.cantidad() == 0
    assert gestor.obtener_fotografias() == ()


def test_agregar_una_fotografia(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    informacion = gestor.agregar_fotografia(ruta)

    assert gestor.cantidad() == 1
    assert informacion.ruta == ruta
    assert informacion.formato == "png"


def test_agregar_multiples_fotografias(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    cantidad = gestor.agregar_fotografias(rutas)

    assert cantidad == 3
    assert gestor.cantidad() == 3


def test_conservar_orden_original(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)

    rutas_obtenidas = [
        foto.ruta
        for foto in gestor.obtener_fotografias()
    ]

    assert rutas_obtenidas == rutas


def test_rechazar_fotografia_duplicada(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    gestor.agregar_fotografia(ruta)

    with pytest.raises(FotografiaDuplicadaError):
        gestor.agregar_fotografia(ruta)

    assert gestor.cantidad() == 1


def test_rechazar_duplicados_en_mismo_lote(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    with pytest.raises(FotografiaDuplicadaError):
        gestor.agregar_fotografias([ruta, ruta])

    assert gestor.cantidad() == 0


def test_lote_invalido_no_modifica_coleccion(tmp_path):
    gestor = GestorFotografias()
    ruta_valida = crear_fotografia(tmp_path / "foto.png")
    ruta_invalida = tmp_path / "inexistente.png"

    with pytest.raises(FileNotFoundError):
        gestor.agregar_fotografias([
            ruta_valida,
            ruta_invalida,
        ])

    assert gestor.cantidad() == 0


def test_error_en_lote_conserva_fotos_anteriores(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografia(rutas[0])

    with pytest.raises(FotografiaDuplicadaError):
        gestor.agregar_fotografias([
            rutas[1],
            rutas[0],
        ])

    assert gestor.cantidad() == 1
    assert gestor.obtener_fotografias()[0].ruta == rutas[0]


def test_quitar_fotografia(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)
    fotografia_quitada = gestor.quitar_fotografia(1)

    assert fotografia_quitada.ruta == rutas[1]
    assert gestor.cantidad() == 2

    rutas_restantes = [
        foto.ruta
        for foto in gestor.obtener_fotografias()
    ]

    assert rutas_restantes == [rutas[0], rutas[2]]


def test_quitar_no_borra_original(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    gestor.agregar_fotografia(ruta)
    gestor.quitar_fotografia(0)

    assert ruta.exists()
    assert gestor.cantidad() == 0


def test_subir_fotografia(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)

    resultado = gestor.subir_fotografia(2)

    assert resultado is True

    orden = [
        foto.ruta
        for foto in gestor.obtener_fotografias()
    ]

    assert orden == [rutas[0], rutas[2], rutas[1]]


def test_bajar_fotografia(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)

    resultado = gestor.bajar_fotografia(0)

    assert resultado is True

    orden = [
        foto.ruta
        for foto in gestor.obtener_fotografias()
    ]

    assert orden == [rutas[1], rutas[0], rutas[2]]


def test_no_subir_primera_fotografia(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)

    assert gestor.subir_fotografia(0) is False


def test_no_bajar_ultima_fotografia(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)

    assert gestor.bajar_fotografia(2) is False


def test_indice_fuera_de_rango(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    gestor.agregar_fotografia(ruta)

    with pytest.raises(FotografiaNoEncontradaError):
        gestor.quitar_fotografia(5)

    with pytest.raises(FotografiaNoEncontradaError):
        gestor.subir_fotografia(-1)


def test_rechazar_indice_no_entero(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    gestor.agregar_fotografia(ruta)

    with pytest.raises(TypeError):
        gestor.bajar_fotografia("0")


def test_vaciar_coleccion_sin_borrar_archivos(tmp_path):
    gestor = GestorFotografias()
    rutas = preparar_tres_fotografias(tmp_path)

    gestor.agregar_fotografias(rutas)
    gestor.vaciar()

    assert gestor.cantidad() == 0
    assert all(ruta.exists() for ruta in rutas)


def test_lista_obtenida_no_puede_modificarse(tmp_path):
    gestor = GestorFotografias()
    ruta = crear_fotografia(tmp_path / "foto.png")

    gestor.agregar_fotografia(ruta)

    fotografias = gestor.obtener_fotografias()

    assert isinstance(fotografias, tuple)

    with pytest.raises(AttributeError):
        fotografias.append("otra_foto")
