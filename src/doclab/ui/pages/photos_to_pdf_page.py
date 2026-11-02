
"""
Pantalla para convertir fotografias en un PDF.

Permite:
- Importar imagenes JPG, JPEG y PNG.
- Ordenar fotografias.
- Quitar imagenes de la seleccion.
- Elegir un destino PDF.
- Generar el documento mediante QThread.

No modifica los archivos originales.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from doclab.document_engine.photo_manager import (
    GestorFotografias,
)

from doclab.workers.photos_to_pdf_worker import (
    TrabajadorFotosPDF,
)


class PaginaFotosPDF(QWidget):
    """Pantalla de digitalizacion de fotografias."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.gestor = GestorFotografias()
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        """Construye los componentes de la pantalla."""

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

        titulo = QLabel("Imágenes a PDF")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Convierte fotografías, apuntes, diapositivas "
            "y otras imágenes en un documento PDF. "
            "Selecciona los archivos, organiza su orden "
            "y genera un único documento."
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setWordWrap(True)

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        # 1. Seleccion de fotografias.
        grupo_fotografias = QGroupBox(
            "1. Seleccionar imagenes"
        )
        contenido_fotografias = QVBoxLayout(
            grupo_fotografias
        )

        explicacion = QLabel(
            "Admite archivos JPG, JPEG y PNG. "
            "Selecciona una o varias fotografías."
        )
        explicacion.setObjectName("textoSecundario")
        explicacion.setWordWrap(True)

        self.boton_agregar = QPushButton(
            "Agregar imágenes"
        )
        self.boton_agregar.clicked.connect(
            self.seleccionar_fotografias
        )

        self.lista_fotografias = QListWidget()
        self.lista_fotografias.setMinimumHeight(180)
        self.lista_fotografias.currentRowChanged.connect(
            self.actualizar_botones
        )

        self.etiqueta_contador = QLabel(
            "0 fotografías seleccionadas"
        )
        self.etiqueta_contador.setObjectName(
            "textoSecundario"
        )

        contenido_fotografias.addWidget(explicacion)
        contenido_fotografias.addWidget(
            self.boton_agregar
        )
        contenido_fotografias.addWidget(
            self.lista_fotografias
        )
        contenido_fotografias.addWidget(
            self.etiqueta_contador
        )

        diseno.addWidget(grupo_fotografias)

        # 2. Orden de las fotografias.
        grupo_organizacion = QGroupBox(
            "2. Organizar imágenes"
        )
        contenido_organizacion = QVBoxLayout(
            grupo_organizacion
        )

        explicacion_orden = QLabel(
            "Selecciona una fotografía y utiliza "
            "los botones para cambiar su posición "
            "o quitarla de la lista. "
            "Los originales no se eliminarán."
        )
        explicacion_orden.setObjectName(
            "textoSecundario"
        )
        explicacion_orden.setWordWrap(True)

        self.boton_subir = QPushButton("Subir")
        self.boton_bajar = QPushButton("Bajar")
        self.boton_quitar = QPushButton("Quitar")

        self.boton_subir.clicked.connect(
            self.subir_fotografia
        )
        self.boton_bajar.clicked.connect(
            self.bajar_fotografia
        )
        self.boton_quitar.clicked.connect(
            self.quitar_fotografia
        )

        fila_botones = QHBoxLayout()
        fila_botones.addWidget(self.boton_subir)
        fila_botones.addWidget(self.boton_bajar)
        fila_botones.addWidget(self.boton_quitar)

        contenido_organizacion.addWidget(
            explicacion_orden
        )
        contenido_organizacion.addLayout(
            fila_botones
        )

        diseno.addWidget(grupo_organizacion)

        # 3. Generacion del PDF.
        grupo_resultado = QGroupBox(
            "3. Generar documento PDF"
        )
        contenido_resultado = QVBoxLayout(
            grupo_resultado
        )

        explicacion_resultado = QLabel(
            "DocLab creará un PDF con una fotografía "
            "por página, respetando el orden elegido. "
            "Esta primera versión no aplica filtros "
            "ni correcciones automáticas."
        )
        explicacion_resultado.setObjectName(
            "textoSecundario"
        )
        explicacion_resultado.setWordWrap(True)

        self.boton_generar = QPushButton(
            "Generar PDF"
        )
        self.boton_generar.setObjectName(
            "botonPrincipal"
        )
        self.boton_generar.clicked.connect(
            self.solicitar_generacion
        )

        contenido_resultado.addWidget(
            explicacion_resultado
        )
        contenido_resultado.addWidget(
            self.boton_generar
        )

        diseno.addWidget(grupo_resultado)

        # 4. Estado de procesamiento.
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.setTextVisible(False)
        self.progreso.setVisible(False)

        self.etiqueta_estado = QLabel("")
        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )
        self.etiqueta_estado.setWordWrap(True)

        diseno.addWidget(self.progreso)
        diseno.addWidget(self.etiqueta_estado)
        diseno.addStretch()

        desplazamiento.setWidget(contenedor)
        diseno_principal.addWidget(desplazamiento)

        self.actualizar_lista()

    def hay_operacion_activa(self):
        """Indica si existe un trabajador pendiente."""
        return self.trabajador is not None

    def seleccionar_fotografias(self):
        """Abre el explorador para seleccionar imagenes."""

        if self.hay_operacion_activa():
            return

        rutas, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar fotografías",
            "",
            "Imágenes (*.jpg *.jpeg *.png)",
        )

        if not rutas:
            return

        try:
            self.agregar_fotografias(rutas)

        except Exception as error:
            QMessageBox.warning(
                self,
                "No fue posible agregar las fotografías",
                str(error),
            )

    def agregar_fotografias(self, rutas):
        """Incorpora imagenes validadas al gestor."""

        if self.hay_operacion_activa():
            raise RuntimeError(
                "Hay una generación PDF en curso."
            )

        cantidad = self.gestor.agregar_fotografias(
            rutas
        )

        self.actualizar_lista()

        self.etiqueta_estado.setText(
            f"Se agregaron {cantidad} fotografía(s)."
        )

        return cantidad

    def actualizar_lista(self, indice_seleccionado=-1):
        """Sincroniza la lista visual con el gestor."""

        self.lista_fotografias.clear()

        fotografias = self.gestor.obtener_fotografias()

        for numero, fotografia in enumerate(
            fotografias,
            start=1,
        ):
            nombre = fotografia.ruta.name

            self.lista_fotografias.addItem(
                f"{numero}. {nombre}"
            )

        cantidad = self.gestor.cantidad()

        self.etiqueta_contador.setText(
            f"{cantidad} fotografía(s) seleccionada(s)"
        )

        if 0 <= indice_seleccionado < cantidad:
            self.lista_fotografias.setCurrentRow(
                indice_seleccionado
            )

        self.actualizar_botones()

    def actualizar_botones(self, indice=None):
        """Habilita acciones segun seleccion y estado."""

        activo = self.hay_operacion_activa()
        cantidad = self.gestor.cantidad()
        posicion = self.lista_fotografias.currentRow()

        self.boton_agregar.setEnabled(not activo)
        self.lista_fotografias.setEnabled(not activo)

        self.boton_subir.setEnabled(
            not activo and posicion > 0
        )

        self.boton_bajar.setEnabled(
            not activo
            and 0 <= posicion < cantidad - 1
        )

        self.boton_quitar.setEnabled(
            not activo and 0 <= posicion < cantidad
        )

        self.boton_generar.setEnabled(
            not activo and cantidad > 0
        )

    def subir_fotografia(self):
        """Mueve la fotografia seleccionada hacia arriba."""

        if self.hay_operacion_activa():
            return

        indice = self.lista_fotografias.currentRow()

        if indice <= 0:
            return

        self.gestor.subir_fotografia(indice)
        self.actualizar_lista(indice - 1)

    def bajar_fotografia(self):
        """Mueve la fotografia seleccionada hacia abajo."""

        if self.hay_operacion_activa():
            return

        indice = self.lista_fotografias.currentRow()

        if indice < 0:
            return

        if indice >= self.gestor.cantidad() - 1:
            return

        self.gestor.bajar_fotografia(indice)
        self.actualizar_lista(indice + 1)

    def quitar_fotografia(self):
        """Quita una imagen sin borrar el original."""

        if self.hay_operacion_activa():
            return

        indice = self.lista_fotografias.currentRow()

        if indice < 0:
            return

        self.gestor.quitar_fotografia(indice)

        nueva_seleccion = min(
            indice,
            self.gestor.cantidad() - 1,
        )

        self.actualizar_lista(nueva_seleccion)

    def solicitar_generacion(self):
        """Permite elegir la ubicacion del PDF."""

        if self.hay_operacion_activa():
            return

        if self.gestor.cantidad() == 0:
            QMessageBox.warning(
                self,
                "Sin fotografías",
                "Agrega al menos una fotografía.",
            )
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar fotografías como PDF",
            "clases_digitalizadas.pdf",
            "Documentos PDF (*.pdf)",
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
                "Ya existe un archivo con ese nombre. "
                "Elige otro destino.",
            )
            return

        self.iniciar_generacion(destino)

    def iniciar_generacion(self, ruta_destino):
        """Inicia el trabajador de forma asincrona."""

        if self.hay_operacion_activa():
            return

        if self.gestor.cantidad() == 0:
            raise ValueError(
                "No hay fotografías para procesar."
            )

        self.trabajador = TrabajadorFotosPDF(
            self.gestor,
            str(ruta_destino),
            parent=self,
        )

        self.trabajador.generacion_exitosa.connect(
            self.mostrar_resultado
        )
        self.trabajador.generacion_fallida.connect(
            self.mostrar_error
        )
        self.trabajador.finished.connect(
            self.finalizar_generacion
        )

        self.actualizar_botones()
        self.progreso.setVisible(True)

        self.etiqueta_estado.setText(
            "Generando documento PDF..."
        )

        self.trabajador.start()

    def mostrar_resultado(self, resultado):
        """Presenta la informacion del PDF generado."""

        self.etiqueta_estado.setText(
            "Documento PDF generado correctamente."
        )

        QMessageBox.information(
            self,
            "Digitalización completada",
            "El documento fue generado correctamente.\n\n"
            f"Páginas: {resultado.numero_paginas}\n"
            f"Tamaño: {resultado.tamano_bytes / 1048576:.2f} MB\n"
            f"Ubicación: {resultado.ruta_destino}\n\n"
            "Te recomendamos revisar las páginas "
            "del documento generado.",
        )

    def mostrar_error(self, mensaje):
        """Informa un problema durante la generacion."""

        self.etiqueta_estado.setText(mensaje)

        QMessageBox.warning(
            self,
            "No se pudo generar el PDF",
            mensaje,
        )

    def finalizar_generacion(self):
        """Libera el trabajador y restaura los controles."""

        trabajador_finalizado = self.trabajador

        self.trabajador = None
        self.progreso.setVisible(False)
        self.actualizar_botones()

        if trabajador_finalizado is not None:
            trabajador_finalizado.deleteLater()

    def closeEvent(self, evento: QCloseEvent):
        """Evita cerrar la pantalla durante una operacion."""

        if self.hay_operacion_activa():
            QMessageBox.warning(
                self,
                "Operación en curso",
                "La generación del PDF todavía "
                "está finalizando.",
            )
            evento.ignore()
            return

        super().closeEvent(evento)
