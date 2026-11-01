
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
    QFrame,
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

        # ---------------------------------------
        # 1. TITULO Y DESCRIPCION
        # ---------------------------------------

        titulo = QLabel(
            "Convertir PDF a Word"
        )

        titulo.setObjectName(
            "tituloPagina"
        )

        descripcion = QLabel(
            "Selecciona un PDF, elige una modalidad "
            "y conviértelo a Word."
        )

        descripcion.setObjectName(
            "textoSecundario"
        )

        descripcion.setWordWrap(True)

        # ---------------------------------------
        # 2. SELECCION DEL ARCHIVO PDF
        # ---------------------------------------

        self.zona_archivos = ZonaArchivos()

        self.zona_archivos.archivo_seleccionado.connect(
            self.establecer_archivo
        )

        self.etiqueta_archivo = QLabel(
            "Ningún documento seleccionado"
        )

        self.etiqueta_archivo.setWordWrap(True)

        # ---------------------------------------
        # 3. SELECTOR DE MODALIDAD
        # ---------------------------------------

        etiqueta_modalidad = QLabel(
            "Modalidad de conversión"
        )

        self.selector_modalidad = QComboBox()

        self.selector_modalidad.addItem(
            "PDF digital - Conversión tradicional",
            "tradicional"
        )

        self.selector_modalidad.addItem(
            "PDF escaneado o con imágenes - OCR",
            "ocr"
        )

        self.selector_modalidad.setToolTip(
            "Selecciona cómo deseas convertir "
            "el documento PDF."
        )

        self.selector_modalidad.currentIndexChanged.connect(
            self.actualizar_descripcion_modalidad
        )

        # ---------------------------------------
        # 4. TARJETA INFORMATIVA
        # ---------------------------------------

        # Primero creamos el contenedor.
        self.tarjeta_modalidad = QFrame()

        self.tarjeta_modalidad.setObjectName(
            "tarjetaModalidad"
        )

        # Aplicamos los estilos al contenedor.
        # setStyleSheet() NO devuelve un widget.
        self.tarjeta_modalidad.setStyleSheet(
            """
            QFrame#tarjetaModalidad {
                background-color: #232230;
                border: 1px solid #514568;
                border-left: 3px solid #A78BFA;
                border-radius: 10px;
            }

            QFrame#tarjetaModalidad QLabel {
                background-color: transparent;
                border: none;
                color: #DDD7EB;
                font-size: 13px;
            }
            """
        )

        # Creamos el diseño interno de la tarjeta.
        diseno_tarjeta = QVBoxLayout(
            self.tarjeta_modalidad
        )

        diseno_tarjeta.setContentsMargins(
            18, 14, 18, 14
        )

        diseno_tarjeta.setSpacing(8)

        # Etiqueta que cambia según la modalidad.
        self.descripcion_modalidad = QLabel()

        self.descripcion_modalidad.setObjectName(
            "textoSecundario"
        )

        self.descripcion_modalidad.setWordWrap(True)

        # Agregamos la etiqueta dentro de la tarjeta.
        diseno_tarjeta.addWidget(
            self.descripcion_modalidad
        )

        # ---------------------------------------
        # 5. BOTON DE CONVERSION
        # ---------------------------------------

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

        # ---------------------------------------
        # 6. BARRA DE PROGRESO
        # ---------------------------------------

        self.progreso = QProgressBar()

        self.progreso.setVisible(False)
        self.progreso.setTextVisible(False)

        # ---------------------------------------
        # 7. ESTADO DE LA CONVERSION
        # ---------------------------------------

        self.etiqueta_estado = QLabel("")

        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )

        self.etiqueta_estado.setWordWrap(True)

        # ---------------------------------------
        # 8. ORGANIZACION VISUAL
        # ---------------------------------------

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

        # CORRECCION:
        # Agregamos el QFrame, no el resultado
        # de llamar a setStyleSheet().
        diseno.addWidget(
            self.tarjeta_modalidad
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

        # Mostrar la descripcion inicial.
        self.actualizar_descripcion_modalidad()

    def actualizar_descripcion_modalidad(self):
        """
        Explica al usuario cuándo utilizar
        cada modalidad de conversión.
        """

        modalidad = self.selector_modalidad.currentData()

        if modalidad == "ocr":

            self.descripcion_modalidad.setText(
                "¿Cuándo elegir esta opción?\n\n"
                "Utilízala cuando tu PDF contenga páginas "
                "escaneadas, fotografías o texto que no "
                "puedas seleccionar con el mouse.\n\n"
                "DocLab intentará reconocer las palabras "
                "para generar un documento Word editable.\n\n"
                "Importante: el reconocimiento puede "
                "contener errores y el diseño original "
                "puede cambiar."
            )

        else:

            self.descripcion_modalidad.setText(
                "¿Cuándo elegir esta opción?\n\n"
                "Utilízala cuando el PDF contenga texto "
                "digital que puedas seleccionar "
                "y copiar con el mouse.\n\n"
                "DocLab convertirá el documento a Word "
                "intentando conservar su distribución "
                "y formato original.\n\n"
                "Importante: el resultado puede presentar "
                "diferencias en tablas, imágenes "
                "o diseños complejos."
            )

    def establecer_archivo(self, ruta):
        """
        Valida el archivo PDF seleccionado
        y actualiza el estado de la interfaz.
        """

        archivo = Path(ruta)

        if (
            not archivo.is_file()
            or archivo.suffix.lower() != ".pdf"
        ):

            QMessageBox.warning(
                self,
                "Archivo no válido",
                "Selecciona un archivo PDF existente."
            )

            return

        self.ruta_pdf = str(archivo)

        self.etiqueta_archivo.setText(
            f"Archivo seleccionado: {archivo.name}"
        )

        self.boton_convertir.setEnabled(True)

    def convertir(self):
        """
        Solicita una ruta de destino
        para el documento Word.
        """

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
        """
        Inicia la conversion mediante
        el trabajador correspondiente.
        """

        if (
            self.trabajador is not None
            and self.trabajador.isRunning()
        ):
            return

        # Bloquear controles durante la conversion.
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
        """
        Informa que la conversion
        termino correctamente.
        """

        self.etiqueta_estado.setText(
            "Conversión finalizada correctamente."
        )

        QMessageBox.information(
            self,
            "Documento Word generado",
            "¡La conversión ha finalizado!\n\n"
            f"Ubicación del documento:\n{ruta}\n\n"
            "Recuerda revisar el contenido y formato "
            "del Word generado, ya que pueden existir "
            "diferencias respecto al PDF original."
        )

    def conversion_con_error(self, mensaje):
        """
        Informa al usuario sobre un error
        ocurrido durante la conversion.
        """

        self.etiqueta_estado.setText(
            "No se pudo convertir el documento."
        )

        QMessageBox.critical(
            self,
            "No se pudo completar la conversión",
            "DocLab encontró un problema al intentar "
            "convertir el PDF a Word.\n\n"
            f"Detalle del problema:\n{mensaje}\n\n"
            "Revisa la información anterior "
            "antes de intentarlo nuevamente."
        )

    def finalizar_trabajo(self):
        """
        Restaura la interfaz cuando
        finaliza la conversion.
        """

        self.progreso.setVisible(False)

        self.zona_archivos.setEnabled(True)

        self.selector_modalidad.setEnabled(True)

        self.boton_convertir.setEnabled(
            bool(self.ruta_pdf)
        )

        self.trabajador = None
