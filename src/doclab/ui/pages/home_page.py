
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.widgets.file_drop_widget import ZonaArchivos


class PaginaInicio(QWidget):

    archivo_seleccionado = Signal(str)
    abrir_conversor = Signal()

    def __init__(self):
        super().__init__()
        self.crear_interfaz()

    def crear_interfaz(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        titulo = QLabel("Bienvenido a DocLab")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Convierte, organiza y transforma tus documentos."
        )
        descripcion.setObjectName("textoSecundario")

        zona_archivos = ZonaArchivos()

        zona_archivos.archivo_seleccionado.connect(
            self.archivo_seleccionado.emit
        )

        subtitulo = QLabel("Herramientas")
        subtitulo.setObjectName("subtituloPagina")

        cuadricula = QGridLayout()
        cuadricula.setSpacing(12)

        herramientas = [
            ("PDF a Word", True),
            ("Unir archivos PDF", False),
            ("Comprimir PDF", False),
            ("Reconocimiento OCR", False),
        ]

        for indice, (nombre, disponible) in enumerate(herramientas):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjetaHerramienta")

            contenido = QVBoxLayout(tarjeta)

            boton = QPushButton(nombre)
            boton.setObjectName("botonHerramienta")
            boton.setEnabled(disponible)

            if disponible:
                boton.clicked.connect(self.abrir_conversor.emit)

            contenido.addWidget(boton)

            if not disponible:
                estado = QLabel("Proximamente")
                estado.setObjectName("textoSecundario")
                contenido.addWidget(estado)

            fila = indice // 2
            columna = indice % 2

            cuadricula.addWidget(tarjeta, fila, columna)

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(zona_archivos)
        diseno.addWidget(subtitulo)
        diseno.addLayout(cuadricula)
        diseno.addStretch()
