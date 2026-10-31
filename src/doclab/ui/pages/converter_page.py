
"""
Pagina de conversion PDF a Word.

Permite elegir entre:
- Conversion tradicional con pdf2docx.
- Conversion avanzada con OCR.

Ambas modalidades se ejecutan sin bloquear
la interfaz grafica.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.widgets.file_drop_widget import (
    ZonaArchivos
)

from doclab.workers.conversion_worker import (
    TrabajadorConversion
)

from doclab.workers.ocr_conversion_worker import (
    TrabajadorConversionOCR
)


class PaginaConversor(QWidget):

    def __init__(self):
        super().__init__()

        self.ruta_pdf = ""
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):

        diseno = QVBoxLayout(self)

        diseno.setContentsMargins(
            32, 32, 32, 32
        )

        diseno.setSpacing(18)

        # 1. Titulo y descripcion.
        titulo = QLabel(
            "Convertir PDF a Word"
        )

        titulo.setObjectName(
            "tituloPagina"
        )

        descripcion = QLabel(
            "Selecciona un PDF, elige una modalidad "
            "y conviertelo a Word."
        )

        descripcion.setObjectName(
            "textoSecundario"
        )

        descripcion.setWordWrap(True)

        # 2. Seleccion del archivo PDF.
        self.zona_archivos = ZonaArchivos()

        self.zona_archivos.archivo_seleccionado.connect(
            self.establecer_archivo
        )

        self.etiqueta_archivo = QLabel(
            "Ningun documento seleccionado"
        )

        self.etiqueta_archivo.setWordWrap(True)

        # 3. Selector de modalidad.
        etiqueta_modalidad = QLabel(
            "Modalidad de conversion"
        )

        self.selector_modalidad = QComboBox()

        self.selector_modalidad.addItem(
            "Tradicional - PDF con texto digital",
            "tradicional"
        )

        self.selector_modalidad.addItem(
            "Con OCR - documentos escaneados o mixtos",
            "ocr"
        )

        self.selector_modalidad.setToolTip(
            "Selecciona como deseas convertir "
            "el documento PDF."
        )

        self.selector_modalidad.currentIndexChanged.connect(
            self.actualizar_descripcion_modalidad
        )

        self.descripcion_modalidad = QLabel()

        self.descripcion_modalidad.setObjectName(
            "textoSecundario"
        )

        self.descripcion_modalidad.setWordWrap(True)

        # 4. Boton de conversion.
        self.boton_convertir = QPushButton(
            "Convertir a Word"
        )

        self.boton_convertir.setObjectName(
            "botonPrincipal"
        )

        self.boton_convertir.setEnabled(False)

        self.boton_convertir.clicked.connect(
            self.convertir
        )

        # 5. Barra de progreso.
        self.progreso = QProgressBar()

        self.progreso.setVisible(False)
        self.progreso.setTextVisible(False)

        # 6. Estado de la conversion.
        self.etiqueta_estado = QLabel("")

        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )

        self.etiqueta_estado.setWordWrap(True)

        # 7. Organizacion visual.
        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        diseno.addWidget(
            self.zona_archivos
        )

        diseno.addWidget(
            self.etiqueta_archivo
        )

        diseno.addWidget(
            etiqueta_modalidad
        )

        diseno.addWidget(
            self.selector_modalidad
        )

        diseno.addWidget(
            self.descripcion_modalidad
        )

        diseno.addWidget(
            self.boton_convertir
        )

        diseno.addWidget(
            self.progreso
        )

        diseno.addWidget(
            self.etiqueta_estado
        )

        diseno.addStretch()

        self.actualizar_descripcion_modalidad()

    def actualizar_descripcion_modalidad(self):

        modalidad = self.selector_modalidad.currentData()

        if modalidad == "ocr":

            self.descripcion_modalidad.setText(
                "Reconoce texto en imagenes y escaneos "
                "para generar un Word editable. "
                "El diseño original puede variar."
            )

        else:

            self.descripcion_modalidad.setText(
                "Convierte PDFs con texto digital "
                "mediante el motor tradicional. "
                "Recomendado para conservar mejor "
                "la distribucion original."
            )

    def establecer_archivo(self, ruta):

        archivo = Path(ruta)

        if (
            not archivo.is_file()
            or archivo.suffix.lower() != ".pdf"
        ):

            QMessageBox.warning(
                self,
                "Archivo no valido",
                "Selecciona un archivo PDF existente."
            )

            return

        self.ruta_pdf = str(archivo)

        self.etiqueta_archivo.setText(
            f"Archivo seleccionado: {archivo.name}"
        )

        self.boton_convertir.setEnabled(True)

    def convertir(self):

        if not self.ruta_pdf:
            return

        if (
            self.trabajador is not None
            and self.trabajador.isRunning()
        ):
            return

        destino_predeterminado = str(
            Path(self.ruta_pdf).with_suffix(".docx")
        )

        ruta_destino, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar documento Word",
            destino_predeterminado,
            "Documentos Word (*.docx)"
        )

        if not ruta_destino:
            return

        if Path(ruta_destino).suffix.lower() != ".docx":
            ruta_destino += ".docx"

        if Path(ruta_destino).exists():

            QMessageBox.warning(
                self,
                "Archivo existente",
                "Elige otro nombre para evitar sobrescribir "
                "un documento existente."
            )

            return

        self.iniciar_conversion(ruta_destino)

    def iniciar_conversion(self, ruta_destino):

        if (
            self.trabajador is not None
            and self.trabajador.isRunning()
        ):
            return

        self.boton_convertir.setEnabled(False)
        self.zona_archivos.setEnabled(False)
        self.selector_modalidad.setEnabled(False)

        self.progreso.setVisible(True)

        # Progreso indeterminado:
        # no disponemos de un porcentaje real.
        self.progreso.setRange(0, 0)

        modalidad = self.selector_modalidad.currentData()

        # Seleccionar el trabajador apropiado.
        if modalidad == "ocr":

            self.etiqueta_estado.setText(
                "Reconociendo texto y generando Word..."
            )

            self.trabajador = TrabajadorConversionOCR(
                self.ruta_pdf,
                ruta_destino
            )

        else:

            self.etiqueta_estado.setText(
                "Convirtiendo documento..."
            )

            self.trabajador = TrabajadorConversion(
                self.ruta_pdf,
                ruta_destino
            )

        # Ambos trabajadores utilizan
        # las mismas señales.
        self.trabajador.conversion_exitosa.connect(
            self.conversion_completada
        )

        self.trabajador.conversion_fallida.connect(
            self.conversion_con_error
        )

        self.trabajador.finished.connect(
            self.finalizar_trabajo
        )

        self.trabajador.start()

    def conversion_completada(self, ruta):

        self.etiqueta_estado.setText(
            "Conversion finalizada correctamente."
        )

        QMessageBox.information(
            self,
            "Conversion completada",
            f"El documento Word se guardo en:\n{ruta}"
        )

    def conversion_con_error(self, mensaje):

        self.etiqueta_estado.setText(
            "No fue posible convertir el documento."
        )

        QMessageBox.critical(
            self,
            "Error de conversion",
            mensaje
        )

    def finalizar_trabajo(self):

        self.progreso.setVisible(False)

        self.zona_archivos.setEnabled(True)

        self.selector_modalidad.setEnabled(True)

        self.boton_convertir.setEnabled(
            bool(self.ruta_pdf)
        )

        self.trabajador = None
