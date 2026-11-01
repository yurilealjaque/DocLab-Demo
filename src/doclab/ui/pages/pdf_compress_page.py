
"""
Pantalla de compresión PDF de DocLab.

Permite seleccionar un PDF, elegir destino
y ejecutar compresión sin pérdida intencional.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from doclab.document_engine.pdf_validator import validar_pdf
from doclab.workers.pdf_compress_worker import TrabajadorCompresionPDF


class PaginaCompresionPDF(QWidget):
    """Interfaz gráfica para optimizar documentos PDF."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ruta_pdf = None
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        """Construye una pantalla desplazable."""

        diseno_principal = QVBoxLayout(self)
        diseno_principal.setContentsMargins(0, 0, 0, 0)

        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setFrameShape(QFrame.Shape.NoFrame)
        desplazamiento.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        contenedor = QWidget()
        diseno = QVBoxLayout(contenedor)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        titulo = QLabel("Comprimir PDF")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Intenta reducir el tamaño de un documento "
            "PDF mediante optimización interna, sin "
            "reducir deliberadamente la calidad de "
            "sus imágenes o textos."
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setWordWrap(True)

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        # 1. Documento original
        grupo_origen = QGroupBox("1. Documento original")
        contenido_origen = QVBoxLayout(grupo_origen)
        contenido_origen.setSpacing(12)

        self.boton_seleccionar = QPushButton(
            "Seleccionar documento PDF"
        )
        self.boton_seleccionar.clicked.connect(
            self.seleccionar_pdf
        )

        self.etiqueta_archivo = QLabel(
            "Ningún documento seleccionado."
        )
        self.etiqueta_archivo.setWordWrap(True)
        self.etiqueta_archivo.setObjectName("textoSecundario")

        self.etiqueta_resumen = QLabel("")
        self.etiqueta_resumen.setObjectName("textoSecundario")

        contenido_origen.addWidget(self.boton_seleccionar)
        contenido_origen.addWidget(self.etiqueta_archivo)
        contenido_origen.addWidget(self.etiqueta_resumen)

        diseno.addWidget(grupo_origen)

        # 2. Explicación de la compresión
        grupo_modalidad = QGroupBox(
            "2. Modalidad de compresión"
        )
        contenido_modalidad = QVBoxLayout(grupo_modalidad)

        explicacion = QLabel(
            "Optimización sin pérdida intencional.\n\n"
            "DocLab intentará reorganizar y comprimir "
            "las estructuras internas del PDF. "
            "No disminuirá deliberadamente la "
            "resolución de sus imágenes.\n\n"
            "Algunos documentos ya están optimizados "
            "y pueden no reducir su tamaño. "
            "Los PDF con posibles firmas digitales "
            "se rechazan preventivamente."
        )
        explicacion.setWordWrap(True)
        explicacion.setObjectName("textoSecundario")

        contenido_modalidad.addWidget(explicacion)
        diseno.addWidget(grupo_modalidad)

        # 3. Destino
        grupo_destino = QGroupBox("3. Guardar resultado")
        contenido_destino = QVBoxLayout(grupo_destino)

        descripcion_destino = QLabel(
            "Selecciona el nombre y la ubicación del "
            "PDF optimizado. El original permanecerá intacto."
        )
        descripcion_destino.setWordWrap(True)
        descripcion_destino.setObjectName("textoSecundario")

        self.boton_comprimir = QPushButton(
            "Comprimir documento PDF"
        )
        self.boton_comprimir.setObjectName("botonPrincipal")
        self.boton_comprimir.setEnabled(False)
        self.boton_comprimir.clicked.connect(
            self.solicitar_compresion
        )

        contenido_destino.addWidget(descripcion_destino)
        contenido_destino.addWidget(self.boton_comprimir)

        diseno.addWidget(grupo_destino)

        # 4. Estado del procesamiento
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.setTextVisible(False)
        self.progreso.setVisible(False)

        self.etiqueta_estado = QLabel("")
        self.etiqueta_estado.setObjectName("textoSecundario")
        self.etiqueta_estado.setWordWrap(True)

        diseno.addWidget(self.progreso)
        diseno.addWidget(self.etiqueta_estado)
        diseno.addStretch()

        desplazamiento.setWidget(contenedor)
        diseno_principal.addWidget(desplazamiento)

    def hay_operacion_activa(self):
        """Indica si existe un trabajador en ejecución."""
        return (
            self.trabajador is not None
            and self.trabajador.isRunning()
        )

    def seleccionar_pdf(self):
        """Abre el explorador de archivos."""
        if self.trabajador is not None:
            return

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar PDF para comprimir",
            "",
            "Documentos PDF (*.pdf)"
        )

        if not ruta:
            return

        try:
            self.cargar_pdf(ruta)
        except Exception as error:
            QMessageBox.warning(
                self,
                "No se pudo cargar el PDF",
                str(error)
            )

    def cargar_pdf(self, ruta):
        """Valida el archivo y muestra su información."""
        if self.trabajador is not None:
            raise RuntimeError(
                "Hay una compresión en proceso."
            )

        paginas = validar_pdf(ruta)
        archivo = Path(ruta)
        tamano = archivo.stat().st_size / (1024 * 1024)

        self.ruta_pdf = str(archivo)
        self.etiqueta_archivo.setText(archivo.name)
        self.etiqueta_archivo.setToolTip(str(archivo))

        self.etiqueta_resumen.setText(
            f"{paginas} página(s) | {tamano:.2f} MB"
        )
        self.etiqueta_estado.setText(
            "Documento cargado correctamente."
        )
        self.boton_comprimir.setEnabled(True)

    def solicitar_compresion(self):
        """Solicita destino y prepara el trabajador."""
        if self.trabajador is not None or not self.ruta_pdf:
            return

        origen = Path(self.ruta_pdf)
        nombre_sugerido = (
            origen.stem + "_comprimido.pdf"
        )

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF comprimido",
            str(origen.parent / nombre_sugerido),
            "Documentos PDF (*.pdf)"
        )

        if not ruta:
            return

        destino = Path(ruta)

        if destino.suffix.lower() != ".pdf":
            destino = Path(str(destino) + ".pdf")

        if destino.exists() or destino.is_symlink():
            QMessageBox.warning(
                self,
                "Archivo existente",
                "El destino ya existe. Selecciona otro nombre."
            )
            return

        if origen.resolve() == destino.resolve():
            QMessageBox.warning(
                self,
                "Destino inválido",
                "No puedes reemplazar el documento original."
            )
            return

        self.iniciar_compresion(str(destino))

    def cambiar_estado_procesamiento(self, activo):
        """Activa o desactiva controles y barra de actividad."""
        self.boton_seleccionar.setEnabled(not activo)
        self.boton_comprimir.setEnabled(
            not activo and self.ruta_pdf is not None
        )
        self.progreso.setVisible(activo)

        if activo:
            self.etiqueta_estado.setText(
                "Optimizando el documento PDF..."
            )

    def iniciar_compresion(self, ruta_destino):
        """Inicia el procesamiento mediante QThread."""
        if self.trabajador is not None:
            return

        self.trabajador = TrabajadorCompresionPDF(
            self.ruta_pdf,
            ruta_destino,
            parent=self
        )

        self.trabajador.compresion_exitosa.connect(
            self.mostrar_resultado
        )
        self.trabajador.compresion_fallida.connect(
            self.mostrar_error
        )
        self.trabajador.finished.connect(
            self.finalizar_compresion
        )

        self.cambiar_estado_procesamiento(True)
        self.trabajador.start()

    def mostrar_resultado(self, resultado):
        """Presenta el ahorro conseguido."""
        original_mb = (
            resultado.tamano_original / (1024 * 1024)
        )
        final_mb = (
            resultado.tamano_final / (1024 * 1024)
        )

        mensaje = (
            "PDF optimizado correctamente.\n\n"
            f"Original: {original_mb:.2f} MB\n"
            f"Optimizado: {final_mb:.2f} MB\n"
            f"Reducción: {resultado.porcentaje_reduccion:.2f}%\n\n"
            f"Guardado en:\n{resultado.ruta_destino}\n\n"
            "Te recomendamos revisar el documento generado."
        )

        self.etiqueta_estado.setText(
            f"Compresión completada. "
            f"Ahorro: {resultado.porcentaje_reduccion:.2f}%"
        )

        QMessageBox.information(
            self,
            "Compresión completada",
            mensaje
        )

    def mostrar_error(self, mensaje):
        """Informa el problema sin ocultar su causa comunicada."""
        self.etiqueta_estado.setText(mensaje)

        QMessageBox.warning(
            self,
            "Compresión no completada",
            mensaje
        )

    def finalizar_compresion(self):
        """Restaura los controles al terminar el trabajador."""
        trabajador_finalizado = self.trabajador

        self.trabajador = None
        self.cambiar_estado_procesamiento(False)

        if trabajador_finalizado is not None:
            trabajador_finalizado.deleteLater()

    def closeEvent(self, evento):
        """Impide cerrar la página durante una operación."""
        if self.trabajador is not None:
            QMessageBox.warning(
                self,
                "Operación en curso",
                "La compresión todavía está finalizando."
            )
            evento.ignore()
            return

        super().closeEvent(evento)
