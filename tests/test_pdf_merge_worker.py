
import doclab.workers.pdf_merge_worker as modulo_trabajador

from doclab.workers.pdf_merge_worker import (
    TrabajadorUnionPDF
)
import threading

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy

def test_trabajador_emite_union_exitosa(monkeypatch):
    """
    Comprueba que el trabajador comunica
    la ruta del PDF generado.
    """

    resultados = []
    errores = []

    class ServicioSimulado:
        def unir(self, origenes, destino):
            assert origenes == ["a.pdf", "b.pdf"]
            assert destino == "resultado.pdf"
            return destino

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioUnionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorUnionPDF(
        ["a.pdf", "b.pdf"],
        "resultado.pdf"
    )

    trabajador.union_exitosa.connect(resultados.append)
    trabajador.union_fallida.connect(errores.append)

    trabajador.run()

    assert resultados == ["resultado.pdf"]
    assert errores == []


def test_trabajador_emite_error_destino_existente(monkeypatch):
    """
    Comprueba que el trabajador transforma
    un error del servicio en una senal.
    """

    resultados = []
    errores = []

    class ServicioSimulado:
        def unir(self, origenes, destino):
            raise FileExistsError("Destino ocupado")

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioUnionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorUnionPDF(
        ["a.pdf", "b.pdf"],
        "resultado.pdf"
    )

    trabajador.union_exitosa.connect(resultados.append)
    trabajador.union_fallida.connect(errores.append)

    trabajador.run()

    assert resultados == []
    assert len(errores) == 1
    assert "ya existe" in errores[0]

def test_trabajador_ejecuta_en_hilo_secundario(monkeypatch):
    """
    Comprueba que start() ejecuta el servicio
    en un hilo diferente al hilo principal.
    """

    aplicacion = QCoreApplication.instance()

    if aplicacion is None:
        aplicacion = QCoreApplication([])

    hilo_principal = threading.get_ident()
    hilos_ejecucion = []

    class ServicioSimulado:
        def unir(self, origenes, destino):
            hilos_ejecucion.append(
                threading.get_ident()
            )
            return destino

    monkeypatch.setattr(
        modulo_trabajador,
        "ServicioUnionPDF",
        ServicioSimulado
    )

    trabajador = TrabajadorUnionPDF(
        ["a.pdf", "b.pdf"],
        "resultado.pdf"
    )

    senal_exitosa = QSignalSpy(
        trabajador.union_exitosa
    )

    senal_fallida = QSignalSpy(
        trabajador.union_fallida
    )

    trabajador.start()

    assert trabajador.wait(5000), (
        "El trabajador no termino dentro "
        "del tiempo esperado."
    )

    aplicacion.processEvents()

    assert len(hilos_ejecucion) == 1
    assert hilos_ejecucion[0] != hilo_principal

    assert senal_exitosa.count() == 1
    assert senal_exitosa.at(0)[0] == "resultado.pdf"
    assert senal_fallida.count() == 0
