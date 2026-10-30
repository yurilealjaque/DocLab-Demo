
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from doclab.ui.widgets.file_drop_widget import ZonaArchivos


class PaginaConversor(QWidget):

    def __init__(self):
        super().__init__()

        self.ruta_pdf = ""
        self.crear_interfaz()

    def crear_interfaz(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        titulo = QLabel("Convertir PDF a Word")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Selecciona un documento PDF para convertirlo."
        )
        descripcion.setObjectName("textoSecundario")

        zona_archivos = ZonaArchivos()

        zona_archivos.archivo_seleccionado.connect(
            self.establecer_archivo
        )

        self.etiqueta_archivo = QLabel(
            "Ningun documento seleccionado"
        )
        self.etiqueta_archivo.setWordWrap(True)

        self.boton_convertir = QPushButton("Convertir a Word")
        self.boton_convertir.setObjectName("botonPrincipal")
        self.boton_convertir.setEnabled(False)

        self.boton_convertir.clicked.connect(
            self.convertir
        )

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(zona_archivos)
        diseno.addWidget(self.etiqueta_archivo)
        diseno.addWidget(self.boton_convertir)
        diseno.addStretch()

    def establecer_archivo(self, ruta):
        archivo = Path(ruta)

        if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
            QMessageBox.warning(
                self,
                "Archivo no valido",
                "Debes seleccionar un archivo PDF existente."
            )
            return

        self.ruta_pdf = str(archivo)
        self.etiqueta_archivo.setText(
            f"Archivo seleccionado: {archivo.name}"
        )
        self.boton_convertir.setEnabled(True)

    def convertir(self):
        ruta_destino, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar documento Word",
            str(Path(self.ruta_pdf).with_suffix(".docx")),
            "Documentos Word (*.docx)"
        )

        if not ruta_destino:
            return

        QMessageBox.information(
            self,
            "Conversion pendiente",
            "Archivo origen:\n"
            f"{self.ruta_pdf}\n\n"
            "Archivo destino:\n"
            f"{ruta_destino}\n\n"
            "Conectaremos el motor de conversion "
            "en la siguiente etapa."
        )
