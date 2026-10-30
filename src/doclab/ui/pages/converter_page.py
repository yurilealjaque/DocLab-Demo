
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.widgets.file_drop_widget import ZonaArchivos
from doclab.workers.conversion_worker import TrabajadorConversion


class PaginaConversor(QWidget):

    def __init__(self):
        super().__init__()

        self.ruta_pdf = ""
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        titulo = QLabel("Convertir PDF a Word")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Selecciona un PDF y conviertelo a Word."
        )
        descripcion.setObjectName("textoSecundario")

        self.zona_archivos = ZonaArchivos()
        self.zona_archivos.archivo_seleccionado.connect(
            self.establecer_archivo
        )

        self.etiqueta_archivo = QLabel(
            "Ningun documento seleccionado"
        )
        self.etiqueta_archivo.setWordWrap(True)

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

        self.progreso = QProgressBar()
        self.progreso.setVisible(False)
        self.progreso.setTextVisible(False)

        self.etiqueta_estado = QLabel("")
        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(self.zona_archivos)
        diseno.addWidget(self.etiqueta_archivo)
        diseno.addWidget(self.boton_convertir)
        diseno.addWidget(self.progreso)
        diseno.addWidget(self.etiqueta_estado)
        diseno.addStretch()

    def establecer_archivo(self, ruta):
        archivo = Path(ruta)

        if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
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
        self.boton_convertir.setEnabled(False)
        self.zona_archivos.setEnabled(False)

        self.progreso.setVisible(True)

        # Rango indeterminado: no conocemos
        # el porcentaje exacto de conversion.
        self.progreso.setRange(0, 0)

        self.etiqueta_estado.setText(
            "Convirtiendo documento..."
        )

        self.trabajador = TrabajadorConversion(
            self.ruta_pdf,
            ruta_destino
        )

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
        self.boton_convertir.setEnabled(
            bool(self.ruta_pdf)
        )

        self.trabajador = None
