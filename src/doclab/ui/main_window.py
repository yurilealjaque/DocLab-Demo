
"""
Ventana principal de DocLab.

Responsabilidades:
- Construir la ventana y el menu lateral.
- Registrar las pantallas de la aplicacion.
- Gestionar la navegacion.
- Recibir las señales de la pantalla de inicio.
- Evitar el cierre durante operaciones activas.
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
from doclab.ui.pages.about_page import PaginaSobreMi


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal de la aplicacion DocLab.
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
        el menu lateral y las pantallas.
        """

        # ---------------------------------------
        # 1. CONTENEDOR PRINCIPAL
        # ---------------------------------------

        contenedor = QWidget()

        diseno_principal = QHBoxLayout(
            contenedor
        )

        diseno_principal.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_principal.setSpacing(0)

        # ---------------------------------------
        # 2. BARRA LATERAL
        # ---------------------------------------

        barra_lateral = QFrame()

        barra_lateral.setObjectName(
            "barraLateral"
        )

        barra_lateral.setFixedWidth(220)

        diseno_lateral = QVBoxLayout(
            barra_lateral
        )

        diseno_lateral.setContentsMargins(
            16, 28, 16, 24
        )

        diseno_lateral.setSpacing(12)

        logo = QLabel("DocLab")
        logo.setObjectName("logo")

        self.boton_inicio = QPushButton(
            "Inicio"
        )

        self.boton_convertir = QPushButton(
            "Convertir"
        )

        self.boton_unir = QPushButton(
            "Unir PDF"
        )

        self.boton_dividir = QPushButton(
            "Dividir PDF"
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
            boton_herramientas,
            boton_historial,
        ]

        for boton in botones_menu:
            boton.setObjectName(
                "botonMenu"
            )

        diseno_lateral.addWidget(logo)
        diseno_lateral.addSpacing(30)

        for boton in botones_menu:
            diseno_lateral.addWidget(
                boton
            )

        boton_herramientas.setEnabled(False)
        boton_historial.setEnabled(False)

        diseno_lateral.addStretch()
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
        # 3. PANTALLAS DE LA APLICACION
        # ---------------------------------------

        self.paginas = QStackedWidget()

        self.pagina_inicio = PaginaInicio()
        self.pagina_conversor = PaginaConversor()
        self.pagina_union = PaginaUnionPDF()
        self.pagina_division = PaginaDivisionPDF()
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
        self.pagina_sobre_mi
        )

        # ---------------------------------------
        # 4. ORGANIZACION PRINCIPAL
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
        # 5. NAVEGACION LATERAL
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

        self.boton_sobre_mi.clicked.connect(
            lambda: self.navegar_a(
                self.pagina_sobre_mi
            )
        )


        # ---------------------------------------
        # 6. NAVEGACION DESDE INICIO
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

        # Ya no existe seleccion de PDF en Inicio.
        # La seleccion se realiza en el conversor.

        # ---------------------------------------
        # 7. PANTALLA INICIAL
        # ---------------------------------------

        self.navegar_a(
            self.pagina_inicio
        )

    def navegar_a(self, pagina):
        """
        Navega a una pantalla registrada.

        Evita utilizar indices fijos,
        facilitando agregar herramientas.
        """

        indice = self.paginas.indexOf(
            pagina
        )

        if indice == -1:
            raise ValueError(
                "La pantalla no esta registrada "
                "en la ventana principal."
            )

        self.mostrar_pagina(
            indice
        )

    def mostrar_pagina(self, indice):
        """
        Cambia la pantalla visible y
        actualiza el estado visual del menu.
        """

        if (
            indice < 0
            or indice >= self.paginas.count()
        ):
            raise ValueError(
                "Indice de pantalla no valido."
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
        operaciones documentales en ejecucion.
        """

        # ---------------------------------------
        # 1. CONVERSION PDF A WORD
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
                "Conversion en proceso",
                "DocLab esta convirtiendo un documento.\n\n"
                "Espera a que termine la conversion "
                "antes de cerrar la aplicacion."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 2. UNION DE DOCUMENTOS PDF
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
                "Union PDF en proceso",
                "DocLab esta uniendo documentos PDF.\n\n"
                "Espera a que termine la union "
                "antes de cerrar la aplicacion."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 3. DIVISION DE DOCUMENTOS PDF
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
                "Division PDF en proceso",
                "DocLab esta dividiendo un documento PDF.\n\n"
                "Espera a que termine la division "
                "antes de cerrar la aplicacion."
            )

            evento.ignore()
            return

        # ---------------------------------------
        # 4. CIERRE SEGURO
        # ---------------------------------------

        evento.accept()
