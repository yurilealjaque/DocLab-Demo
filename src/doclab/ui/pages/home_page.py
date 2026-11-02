"""
Pantalla de inicio de DocLab.

Responsabilidades:
- Dar la bienvenida al usuario.
- Presentar las herramientas disponibles.
- Explicar para que sirve cada herramienta.
- Permitir navegar a las distintas herramientas documentales.
- Identificar funcionalidades futuras.

La seleccion de archivos se realiza en cada herramienta.
"""

from PySide6.QtCore import Signal, Qt

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class PaginaInicio(QWidget):
    """Pantalla principal de bienvenida de DocLab."""

    abrir_conversor = Signal()
    abrir_union_pdf = Signal()
    abrir_division_pdf = Signal()
    abrir_compresion_pdf = Signal()
    abrir_fotografias_pdf = Signal()

    def __init__(self):
        super().__init__()
        self.crear_interfaz()

    def crear_tarjeta(
        self,
        icono,
        nombre,
        descripcion,
        disponible=True,
        accion=None,
    ):
        """Construye una tarjeta descriptiva para una herramienta."""
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaHerramienta")
        tarjeta.setMinimumHeight(185)

        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(20, 18, 20, 18)
        contenido.setSpacing(10)

        encabezado = QHBoxLayout()
        encabezado.setSpacing(12)

        etiqueta_icono = QLabel(icono)
        etiqueta_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        etiqueta_icono.setFixedSize(44, 44)
        etiqueta_icono.setStyleSheet(
            "background-color: #35264F;"
            "color: #D8C8FF;"
            "border-radius: 10px;"
            "font-size: 18px;"
            "font-weight: bold;"
        )

        etiqueta_nombre = QLabel(nombre)
        etiqueta_nombre.setWordWrap(True)
        etiqueta_nombre.setStyleSheet(
            "color: #F5F3FF;"
            "font-size: 17px;"
            "font-weight: bold;"
            "background: transparent;"
        )

        encabezado.addWidget(etiqueta_icono)
        encabezado.addWidget(etiqueta_nombre, 1)
        contenido.addLayout(encabezado)

        etiqueta_descripcion = QLabel(descripcion)
        etiqueta_descripcion.setWordWrap(True)
        etiqueta_descripcion.setAlignment(Qt.AlignmentFlag.AlignTop)
        etiqueta_descripcion.setObjectName("textoSecundario")

        contenido.addWidget(etiqueta_descripcion)
        contenido.addStretch()

        if disponible:
            boton = QPushButton("Abrir herramienta")
            boton.setObjectName("botonPrincipal")
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            if accion is not None:
                boton.clicked.connect(accion)
        else:
            boton = QPushButton("Próximamente")
            boton.setEnabled(False)
            tarjeta.setToolTip(
                "Esta herramienta todavía no se encuentra disponible."
            )

        contenido.addWidget(boton)
        return tarjeta

    def crear_interfaz(self):
        """Construye la bienvenida y el catalogo de herramientas."""
        diseno_principal = QVBoxLayout(self)
        diseno_principal.setContentsMargins(0, 0, 0, 0)
        diseno_principal.setSpacing(0)

        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setFrameShape(QFrame.Shape.NoFrame)

        contenedor = QWidget()
        diseno = QVBoxLayout(contenedor)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        # 1. Bienvenida.
        titulo = QLabel("Bienvenido a DocLab")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Tu espacio de trabajo para convertir, "
            "organizar y transformar documentos."
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setWordWrap(True)

        instruccion = QLabel(
            "Selecciona una herramienta para comenzar. "
            "Cada opción te llevará a su espacio de trabajo."
        )
        instruccion.setWordWrap(True)
        instruccion.setStyleSheet(
            "color: #D8D2E5;"
            "font-size: 14px;"
            "background: transparent;"
        )

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(instruccion)
        diseno.addSpacing(12)

        # 2. Herramientas disponibles.
        subtitulo = QLabel("Herramientas disponibles")
        subtitulo.setObjectName("subtituloPagina")
        diseno.addWidget(subtitulo)

        cuadricula = QGridLayout()
        cuadricula.setSpacing(16)

        tarjeta_convertir = self.crear_tarjeta(
            "W",
            "Convertir PDF a Word",
            "Transforma documentos PDF en archivos Word editables. "
            "Puedes utilizar la conversión tradicional o el "
            "reconocimiento de texto mediante OCR.",
            accion=self.abrir_conversor.emit,
        )

        tarjeta_unir = self.crear_tarjeta(
            "+",
            "Unir archivos PDF",
            "Combina dos o más documentos PDF en un único archivo. "
            "Puedes elegir el orden de los documentos antes de realizar la unión.",
            accion=self.abrir_union_pdf.emit,
        )

        tarjeta_dividir = self.crear_tarjeta(
            "÷",
            "Dividir archivos PDF",
            "Extrae un rango de páginas, selecciona páginas específicas "
            "o genera un PDF independiente por cada página.",
            accion=self.abrir_division_pdf.emit,
        )

        tarjeta_comprimir = self.crear_tarjeta(
            "↓",
            "Comprimir PDF",
            "Intenta reducir el tamaño de tus documentos PDF mediante "
            "optimización interna, sin disminuir deliberadamente la "
            "calidad de sus imágenes o textos.",
            accion=self.abrir_compresion_pdf.emit,
        )

        tarjeta_fotos = self.crear_tarjeta(
            "▣",
            "Imágenes a PDF",
            "Convierte fotografías, diapositivas, "
            "apuntes y otras imágenes en un documento "
            "PDF. Organiza los archivos en el orden "
            "que prefieras antes de generar el resultado.",
            accion=self.abrir_fotografias_pdf.emit
        )

        self.tarjeta_convertir = tarjeta_convertir
        self.tarjeta_unir = tarjeta_unir
        self.tarjeta_dividir = tarjeta_dividir
        self.tarjeta_comprimir = tarjeta_comprimir
        self.tarjeta_fotos = tarjeta_fotos

        cuadricula.addWidget(tarjeta_convertir, 0, 0)
        cuadricula.addWidget(tarjeta_unir, 0, 1)
        cuadricula.addWidget(tarjeta_dividir, 1, 0)
        cuadricula.addWidget(tarjeta_comprimir, 1, 1)
        cuadricula.addWidget(tarjeta_fotos, 2, 0)

        cuadricula.setColumnStretch(0, 1)
        cuadricula.setColumnStretch(1, 1)
        diseno.addLayout(cuadricula)

        # 3. Funcionalidades futuras.
        # La tarjeta de fotografias ya NO aparece en esta seccion.
        diseno.addSpacing(12)
        subtitulo_futuras = QLabel("Próximamente")
        subtitulo_futuras.setObjectName("subtituloPagina")

        descripcion_futuras = QLabel(
            "Seguiremos incorporando nuevas herramientas de "
            "procesamiento documental en futuras versiones de DocLab."
        )
        descripcion_futuras.setObjectName("textoSecundario")
        descripcion_futuras.setWordWrap(True)

        diseno.addWidget(subtitulo_futuras)
        diseno.addWidget(descripcion_futuras)
        diseno.addStretch()

        desplazamiento.setWidget(contenedor)
        diseno_principal.addWidget(desplazamiento)
