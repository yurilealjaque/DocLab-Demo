
"""
Pantalla de inicio de DocLab.

Presenta las herramientas disponibles
y permite navegar hacia sus respectivas pantallas.
"""

from PySide6.QtCore import Signal

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
    """
    Pantalla principal de bienvenida de DocLab.
    """

    archivo_seleccionado = Signal(str)
    abrir_conversor = Signal()
    abrir_union_pdf = Signal()

    def __init__(self):
        super().__init__()

        self.crear_interfaz()

    def crear_interfaz(self):
        """
        Construye los componentes visuales
        de la pantalla de inicio.
        """

        diseno = QVBoxLayout(self)

        diseno.setContentsMargins(
            32, 32, 32, 32
        )

        diseno.setSpacing(18)

        # 1. Titulo de bienvenida.
        titulo = QLabel(
            "Bienvenido a DocLab"
        )

        titulo.setObjectName(
            "tituloPagina"
        )

        # 2. Descripcion general.
        descripcion = QLabel(
            "Convierte, organiza y transforma tus documentos."
        )

        descripcion.setObjectName(
            "textoSecundario"
        )

        # 3. Zona para seleccionar archivos PDF.
        zona_archivos = ZonaArchivos()

        zona_archivos.archivo_seleccionado.connect(
            self.archivo_seleccionado.emit
        )

        # 4. Titulo de herramientas.
        subtitulo = QLabel(
            "Herramientas"
        )

        subtitulo.setObjectName(
            "subtituloPagina"
        )

        # 5. Cuadricula de herramientas.
        cuadricula = QGridLayout()
        cuadricula.setSpacing(12)

        herramientas = [
            ("PDF a Word", True),
            ("Unir archivos PDF", True),
            ("Comprimir PDF", False),
            ("Reconocimiento OCR", False),
        ]

        for indice, (nombre, disponible) in enumerate(
            herramientas
        ):
            tarjeta = QFrame()

            tarjeta.setObjectName(
                "tarjetaHerramienta"
            )

            contenido = QVBoxLayout(
                tarjeta
            )

            boton = QPushButton(
                nombre
            )

            boton.setObjectName(
                "botonHerramienta"
            )

            boton.setEnabled(
                disponible
            )

            # Cada herramienta dirige a su pantalla.
            if nombre == "PDF a Word":
                boton.clicked.connect(
                    self.abrir_conversor.emit
                )

            elif nombre == "Unir archivos PDF":
                boton.clicked.connect(
                    self.abrir_union_pdf.emit
                )

            contenido.addWidget(
                boton
            )

            # Mostrar estado de herramientas futuras.
            if not disponible:
                estado = QLabel(
                    "Proximamente"
                )

                estado.setObjectName(
                    "textoSecundario"
                )

                contenido.addWidget(
                    estado
                )

            # Distribuir las tarjetas en dos columnas.
            fila = indice // 2
            columna = indice % 2

            cuadricula.addWidget(
                tarjeta,
                fila,
                columna
            )

        # 6. Organizacion de la pantalla.
        diseno.addWidget(
            titulo
        )

        diseno.addWidget(
            descripcion
        )

        diseno.addWidget(
            zona_archivos
        )

        diseno.addWidget(
            subtitulo
        )

        diseno.addLayout(
            cuadricula
        )

        diseno.addStretch()
