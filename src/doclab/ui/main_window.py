

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.pages.home_page import PaginaInicio
from doclab.ui.pages.converter_page import PaginaConversor
from PySide6.QtWidgets import QMessageBox


class VentanaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DocLab - Laboratorio documental")
        self.resize(1100, 720)
        self.setMinimumSize(760, 580)

        self.crear_interfaz()

    def crear_interfaz(self):
        contenedor = QWidget()
        diseno_principal = QHBoxLayout(contenedor)

        diseno_principal.setContentsMargins(0, 0, 0, 0)
        diseno_principal.setSpacing(0)

        # Menu lateral
        barra_lateral = QFrame()
        barra_lateral.setObjectName("barraLateral")
        barra_lateral.setFixedWidth(220)

        diseno_lateral = QVBoxLayout(barra_lateral)
        diseno_lateral.setContentsMargins(16, 28, 16, 24)
        diseno_lateral.setSpacing(12)

        logo = QLabel("DocLab")
        logo.setObjectName("logo")

        self.boton_inicio = QPushButton("Inicio")
        self.boton_convertir = QPushButton("Convertir")

        boton_herramientas = QPushButton("Herramientas")
        boton_historial = QPushButton("Historial")

        for boton in [
            self.boton_inicio,
            self.boton_convertir,
            boton_herramientas,
            boton_historial,
        ]:
            boton.setObjectName("botonMenu")
            diseno_lateral.addWidget(boton)

        boton_herramientas.setEnabled(False)
        boton_historial.setEnabled(False)

        diseno_lateral.insertWidget(0, logo)
        diseno_lateral.insertSpacing(1, 30)
        diseno_lateral.addStretch()

        # Pantallas de la aplicacion
        self.paginas = QStackedWidget()

        self.pagina_inicio = PaginaInicio()
        self.pagina_conversor = PaginaConversor()

        self.paginas.addWidget(self.pagina_inicio)
        self.paginas.addWidget(self.pagina_conversor)

        diseno_principal.addWidget(barra_lateral)
        diseno_principal.addWidget(self.paginas, 1)

        self.setCentralWidget(contenedor)

        # Conexiones de navegacion
        self.boton_inicio.clicked.connect(
            lambda: self.mostrar_pagina(0)
        )

        self.boton_convertir.clicked.connect(
            lambda: self.mostrar_pagina(1)
        )

        self.pagina_inicio.abrir_conversor.connect(
            lambda: self.mostrar_pagina(1)
        )

        self.pagina_inicio.archivo_seleccionado.connect(
            self.abrir_archivo_en_conversor
        )

        self.mostrar_pagina(0)



    def mostrar_pagina(self, indice):
        self.paginas.setCurrentIndex(indice)

        self.boton_inicio.setProperty(
            "activo", indice == 0
        )
        self.boton_convertir.setProperty(
            "activo", indice == 1
        )

        for boton in [
            self.boton_inicio,
            self.boton_convertir,
        ]:
            boton.style().unpolish(boton)
            boton.style().polish(boton)
            boton.update()

    def abrir_archivo_en_conversor(self, ruta):
        self.pagina_conversor.establecer_archivo(ruta)

        if self.pagina_conversor.ruta_pdf == ruta:
            self.mostrar_pagina(1)

    def closeEvent(self, evento):
        trabajador = self.pagina_conversor.trabajador

        if trabajador is not None and trabajador.isRunning():
            QMessageBox.warning(
                self,
                "Conversion en proceso",
                "DocLab esta convirtiendo un documento.\n\n"
                "Para evitar interrupciones, espera a que "
                "termine la conversion antes de cerrar."
            )

            evento.ignore()
            return

        evento.accept()
