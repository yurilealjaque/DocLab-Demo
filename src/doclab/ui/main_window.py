"""
Ventana principal de DocLab.

Responsabilidades:
- Construir la ventana y el menú lateral.
- Registrar las pantallas de la aplicación.
- Gestionar la navegación.
- Recibir las señales de la pantalla de inicio.
- Evitar el cierre durante operaciones activas.

Herramientas:
- Convertir PDF a Word.
- Unir documentos PDF.
- Dividir documentos PDF.
- Comprimir documentos PDF.
- Digitalizar clases a partir de fotografías.
- Sobre mí.
"""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.pages.home_page import PaginaInicio
from doclab.ui.pages.converter_page import PaginaConversor
from doclab.ui.pages.pdf_merge_page import PaginaUnionPDF
from doclab.ui.pages.pdf_split_page import PaginaDivisionPDF
from doclab.ui.pages.pdf_compress_page import PaginaCompresionPDF
from doclab.ui.pages.about_page import PaginaSobreMi
from doclab.ui.pages.photos_to_pdf_page import PaginaFotosPDF


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal de la aplicación DocLab.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "DocLab - Laboratorio documental"
        )

        self.resize(1100, 720)
        self.setMinimumSize(760, 580)

        self.crear_interfaz()

    def crear_interfaz(self):
        """
        Construye la interfaz principal,
        el menú lateral y las pantallas.
        """

        # ---------------------------------------
        # 1. CONTENEDOR PRINCIPAL
        # ---------------------------------------

        contenedor = QWidget()

        diseno_principal = QHBoxLayout(contenedor)

        diseno_principal.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_principal.setSpacing(0)

        # ---------------------------------------
        # 2. BARRA LATERAL
        # ---------------------------------------

        barra_lateral = QFrame()
        barra_lateral.setObjectName("barraLateral")
        barra_lateral.setFixedWidth(220)

        diseno_lateral = QVBoxLayout(barra_lateral)

        diseno_lateral.setContentsMargins(
            16, 28, 16, 24
        )

        diseno_lateral.setSpacing(12)

        logo = QLabel("DocLab")
        logo.setObjectName("logo")

        # Botones de las herramientas.
        self.boton_inicio = QPushButton("Inicio")

        self.boton_convertir = QPushButton(
            "Convertir"
        )

        self.boton_unir = QPushButton(
            "Unir PDF"
        )

        self.boton_dividir = QPushButton(
            "Dividir PDF"
        )

        self.boton_comprimir = QPushButton(
            "Comprimir PDF"
        )

        self.boton_fotografias = QPushButton(
            "Imágenes a PDF"
        )

        boton_herramientas = QPushButton(
            "Herramientas"
        )

        boton_historial = QPushButton(
            "Historial"
        )

        botones_menu = [
            self.boton_inicio,
            self.boton_convertir,
            self.boton_unir,
            self.boton_dividir,
            self.boton_comprimir,
            self.boton_fotografias,
            boton_herramientas,
            boton_historial,
        ]

        for boton in botones_menu:
            boton.setObjectName("botonMenu")

        diseno_lateral.addWidget(logo)
        diseno_lateral.addSpacing(30)

        for boton in botones_menu:
            diseno_lateral.addWidget(boton)

        # Funcionalidades todavía no implementadas.
        boton_herramientas.setEnabled(False)
        boton_historial.setEnabled(False)

        diseno_lateral.addStretch()

        # ---------------------------------------
        # BOTÓN SOBRE MÍ
        # ---------------------------------------

        self.boton_sobre_mi = QPushButton(
            "Sobre mí"
        )

        self.boton_sobre_mi.setObjectName(
            "botonMenu"
        )

        diseno_lateral.addWidget(
            self.boton_sobre_mi
        )

        # ---------------------------------------
        # 3. PANTALLAS DE LA APLICACIÓN
        # ---------------------------------------

        self.paginas = QStackedWidget()

        self.pagina_inicio = PaginaInicio()
        self.pagina_conversor = PaginaConversor()
        self.pagina_union = PaginaUnionPDF()
        self.pagina_division = PaginaDivisionPDF()
        self.pagina_compresion = PaginaCompresionPDF()
        self.pagina_fotografias = PaginaFotosPDF()
        self.pagina_sobre_mi = PaginaSobreMi()

        self.paginas.addWidget(
            self.pagina_inicio
        )

        self.paginas.addWidget(
            self.pagina_conversor
        )

        self.paginas.addWidget(
            self.pagina_union
        )

        self.paginas.addWidget(
            self.pagina_division
        )

        self.paginas.addWidget(
            self.pagina_compresion
        )

        self.paginas.addWidget(
            self.pagina_fotografias
        )

        self.paginas.addWidget(
            self.pagina_sobre_mi
        )

        # ---------------------------------------
        # 4. ORGANIZACIÓN PRINCIPAL
        # ---------------------------------------

        diseno_principal.addWidget(
            barra_lateral
        )

        diseno_principal.addWidget(
            self.paginas,
            1
        )

        self.setCentralWidget(
            contenedor
        )

        # ---------------------------------------
        # 5. NAVEGACIÓN LATERAL
        # ---------------------------------------

        self.boton_inicio.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_inicio
            )
        )

        self.boton_convertir.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_conversor
            )
        )

        self.boton_unir.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_union
            )
        )

        self.boton_dividir.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_division
            )
        )

        self.boton_comprimir.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_compresion
            )
        )

        self.boton_fotografias.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_fotografias
            )
        )

        self.boton_sobre_mi.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_sobre_mi
            )
        )

        # ---------------------------------------
        # 6. NAVEGACIÓN DESDE INICIO
        # ---------------------------------------

        self.pagina_inicio.abrir_conversor.connect(
            lambda: self.navegar_a(
                self.pagina_conversor
            )
        )

        self.pagina_inicio.abrir_union_pdf.connect(
            lambda: self.navegar_a(
                self.pagina_union
            )
        )

        self.pagina_inicio.abrir_division_pdf.connect(
            lambda: self.navegar_a(
                self.pagina_division
            )
        )

        self.pagina_inicio.abrir_compresion_pdf.connect(
            lambda: self.navegar_a(
                self.pagina_compresion
            )
        )

        self.pagina_inicio.abrir_fotografias_pdf.connect(
            lambda: self.navegar_a(
                self.pagina_fotografias
            )
        )

        # ---------------------------------------
        # 7. PANTALLA INICIAL
        # ---------------------------------------

        self.navegar_a(
            self.pagina_inicio
        )

    def navegar_a(self, pagina):
        """
        Navega a una pantalla registrada.

        Evita utilizar índices fijos para
        facilitar la incorporación de herramientas.
        """

        indice = self.paginas.indexOf(
            pagina
        )

        if indice == -1:
            raise ValueError(
                "La pantalla no está registrada "
                "en la ventana principal."
            )

        self.mostrar_pagina(
            indice
        )

    def mostrar_pagina(self, indice):
        """
        Cambia la pantalla visible y actualiza
        el estado visual del menú lateral.
        """

        if (
            indice < 0
            or indice >= self.paginas.count()
        ):
            raise ValueError(
                "Índice de pantalla no válido."
            )

        self.paginas.setCurrentIndex(
            indice
        )

        navegacion = [
            (
                self.boton_inicio,
                self.pagina_inicio
            ),
            (
                self.boton_convertir,
                self.pagina_conversor
            ),
            (
                self.boton_unir,
                self.pagina_union
            ),
            (
                self.boton_dividir,
                self.pagina_division
            ),
            (
                self.boton_comprimir,
                self.pagina_compresion
            ),
            (
                self.boton_fotografias,
                self.pagina_fotografias
            ),
            (
                self.boton_sobre_mi,
                self.pagina_sobre_mi
            ),
        ]

        for boton, pagina in navegacion:

            esta_activo = (
                self.paginas.currentWidget()
                is pagina
            )

            boton.setProperty(
                "activo",
                esta_activo
            )

            boton.style().unpolish(
                boton
            )

            boton.style().polish(
                boton
            )

            boton.update()

    def closeEvent(self, evento):
        """
        Impide cerrar DocLab mientras existan
        operaciones documentales en ejecución.
        """

        # ---------------------------------------
        # 1. CONVERSIÓN PDF A WORD
        # ---------------------------------------

        trabajador_conversion = (
            self.pagina_conversor.trabajador
        )

        if (
            trabajador_conversion is not None
            and trabajador_conversion.isRunning()
        ):
            QMessageBox.warning(
                self,
                "Conversión en proceso",
                "DocLab está convirtiendo un documento.\n\n"
                "Espera a que termine la conversión "
                "antes de cerrar la aplicación."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 2. UNIÓN DE DOCUMENTOS PDF
        # ---------------------------------------

        trabajador_union = (
            self.pagina_union.trabajador
        )

        if (
            trabajador_union is not None
            and trabajador_union.isRunning()
        ):
            QMessageBox.warning(
                self,
                "Unión PDF en proceso",
                "DocLab está uniendo documentos PDF.\n\n"
                "Espera a que termine la unión "
                "antes de cerrar la aplicación."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 3. DIVISIÓN DE DOCUMENTOS PDF
        # ---------------------------------------

        trabajador_division = (
            self.pagina_division.trabajador
        )

        if (
            trabajador_division is not None
            and trabajador_division.isRunning()
        ):
            QMessageBox.warning(
                self,
                "División PDF en proceso",
                "DocLab está dividiendo un documento PDF.\n\n"
                "Espera a que termine la división "
                "antes de cerrar la aplicación."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 4. COMPRESIÓN DE DOCUMENTOS PDF
        # ---------------------------------------

        trabajador_compresion = (
            self.pagina_compresion.trabajador
        )

        if trabajador_compresion is not None:
            QMessageBox.warning(
                self,
                "Compresión PDF en proceso",
                "DocLab está comprimiendo un documento PDF "
                "o finalizando la operación.\n\n"
                "Espera a que termine el procesamiento "
                "antes de cerrar la aplicación."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 5. DIGITALIZACIÓN DE CLASES
        # ---------------------------------------

        if self.pagina_fotografias.hay_operacion_activa():
            QMessageBox.warning(
            self,
            "Conversión de imágenes en proceso",
            "DocLab está convirtiendo imágenes a PDF "
            "o finalizando la operación.\n\n"
            "Espera a que termine el procesamiento "
            "antes de cerrar la aplicación."
        )
            evento.ignore()
            return

        # ---------------------------------------
        # 6. CIERRE SEGURO
        # ---------------------------------------

        evento.accept()
