
import pytest

import doclab.services.pdf_merge_service as modulo_servicio

from doclab.services.pdf_merge_service import (
    ServicioUnionPDF
)


def test_servicio_delega_union_al_motor(monkeypatch):
    """
    Comprueba que el servicio llama al motor
    con los argumentos correctos.
    """

    rutas_origen = ["primero.pdf", "segundo.pdf"]
    ruta_destino = "resultado.pdf"

    llamadas = []

    def motor_simulado(origenes, destino):
        llamadas.append((origenes, destino))
        return destino

    monkeypatch.setattr(
        modulo_servicio,
        "unir_archivos_pdf",
        motor_simulado
    )

    servicio = ServicioUnionPDF()

    resultado = servicio.unir(
        rutas_origen,
        ruta_destino
    )

    assert resultado == ruta_destino
    assert llamadas == [
        (rutas_origen, ruta_destino)
    ]


def test_servicio_propaga_error_del_motor(monkeypatch):
    """
    Comprueba que el servicio no oculta
    los errores producidos por el motor.
    """

    def motor_con_error(origenes, destino):
        raise FileExistsError(
            "El documento de destino ya existe."
        )

    monkeypatch.setattr(
        modulo_servicio,
        "unir_archivos_pdf",
        motor_con_error
    )

    servicio = ServicioUnionPDF()

    with pytest.raises(
        FileExistsError,
        match="El documento de destino ya existe"
    ):
        servicio.unir(
            ["primero.pdf", "segundo.pdf"],
            "resultado.pdf"
        )
