"""Pantalla de unión de archivos PDF de DocLab.

Permite seleccionar, ordenar y quitar documentos, consultar su resumen,
y unirlos mediante un trabajador QThread sin bloquear la interfaz.
"""

from pathlib import Path

import pymupdf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from doclab.workers.pdf_merge_worker import TrabajadorUnionPDF


class PaginaUnionPDF(QWidget):
    """Permite preparar y ejecutar la unión de archivos PDF."""

    def __init__(self):
        super().__init__()
        self.rutas_pdf = []
        self.trabajador = None
        self.crear_interfaz()

    def crear_interfaz(self):
        """Construye una pantalla desplazable, sin solapamientos."""
        diseno_exterior = QVBoxLayout(self)
        diseno_exterior.setContentsMargins(0, 0, 0, 0)

        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setFrameShape(QFrame.Shape.NoFrame)
        desplazamiento.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        diseno_exterior.addWidget(desplazamiento)

        contenido = QWidget()
        desplazamiento.setWidget(contenido)

        diseno = QVBoxLayout(contenido)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(14)

        titulo = QLabel("Unir documentos PDF")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Combina dos o más documentos PDF en un solo archivo, "
            "respetando el orden que elijas."
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setWordWrap(True)

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addSpacing(8)

        etiqueta_seleccion = QLabel("1. Selecciona tus documentos")
        etiqueta_seleccion.setObjectName("subtituloPagina")
        descripcion_seleccion = QLabel(
            "Agrega al menos dos archivos PDF. Puedes seleccionar "
            "varios documentos al mismo tiempo."
        )
        descripcion_seleccion.setObjectName("textoSecundario")
        descripcion_seleccion.setWordWrap(True)

        self.boton_agregar = QPushButton("Agregar archivos PDF")
        self.boton_agregar.setToolTip(
            "Selecciona los documentos PDF que deseas combinar."
        )
        self.boton_agregar.clicked.connect(self.seleccionar_archivos)

        diseno.addWidget(etiqueta_seleccion)
        diseno.addWidget(descripcion_seleccion)
        diseno.addWidget(self.boton_agregar)

        # El QStackedWidget tiene altura fija para que la vista vacía
        # y la lista ocupen el mismo lugar sin solapar otros controles.
        self.contenedor_documentos = QStackedWidget()
        self.contenedor_documentos.setFixedHeight(205)

        self.estado_vacio = QFrame()
        self.estado_vacio.setObjectName("estadoVacio")
        diseno_vacio = QVBoxLayout(self.estado_vacio)
        diseno_vacio.setContentsMargins(18, 16, 18, 16)
        diseno_vacio.setSpacing(7)

        icono_vacio = QLabel("PDF")
        icono_vacio.setObjectName("iconoEstadoVacio")
        icono_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo_vacio = QLabel("Todavía no hay documentos")
        titulo_vacio.setObjectName("tituloEstadoVacio")
        titulo_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)

        descripcion_vacio = QLabel(
            "Los archivos que agregues aparecerán aquí. "
            "Podrás cambiar su orden o quitarlos de la lista."
        )
        descripcion_vacio.setObjectName("textoEstadoVacio")
        descripcion_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descripcion_vacio.setWordWrap(True)

        diseno_vacio.addStretch()
        diseno_vacio.addWidget(icono_vacio)
        diseno_vacio.addWidget(titulo_vacio)
        diseno_vacio.addWidget(descripcion_vacio)
        diseno_vacio.addStretch()

        self.lista_archivos = QListWidget()
        self.lista_archivos.setToolTip(
            "Selecciona un documento para cambiar su posición o quitarlo."
        )
        self.lista_archivos.currentRowChanged.connect(
            self.actualizar_estado_botones
        )
        self.contenedor_documentos.addWidget(self.estado_vacio)
        self.contenedor_documentos.addWidget(self.lista_archivos)
        diseno.addWidget(self.contenedor_documentos)

        self.etiqueta_orden = QLabel("2. Organiza tus documentos")
        self.etiqueta_orden.setObjectName("subtituloPagina")
        self.descripcion_orden = QLabel(
            "Selecciona un archivo de la lista. Usa Subir o Bajar para "
            "cambiar su posición en el documento final."
        )
        self.descripcion_orden.setObjectName("textoSecundario")
        self.descripcion_orden.setWordWrap(True)

        self.boton_subir = QPushButton("Subir")
        self.boton_bajar = QPushButton("Bajar")
        self.boton_eliminar = QPushButton("Eliminar")

        self.boton_subir.setToolTip(
            "Mueve el documento seleccionado una posición hacia arriba."
        )
        self.boton_bajar.setToolTip(
            "Mueve el documento seleccionado una posición hacia abajo."
        )
        self.boton_eliminar.setToolTip(
            "Quita el documento de la lista, sin borrarlo del computador."
        )
        self.boton_subir.clicked.connect(self.subir_archivo)
        self.boton_bajar.clicked.connect(self.bajar_archivo)
        self.boton_eliminar.clicked.connect(self.eliminar_archivo)

        diseno_botones = QHBoxLayout()
        diseno_botones.setSpacing(12)
        diseno_botones.addWidget(self.boton_subir)
        diseno_botones.addWidget(self.boton_bajar)
        diseno_botones.addWidget(self.boton_eliminar)

        diseno.addWidget(self.etiqueta_orden)
        diseno.addWidget(self.descripcion_orden)
        diseno.addLayout(diseno_botones)

        self.etiqueta_contador = QLabel("0 archivos seleccionados")
        self.etiqueta_contador.setObjectName("textoSecundario")
        self.etiqueta_resumen = QLabel("0 páginas | 0.00 MB")
        self.etiqueta_resumen.setObjectName("textoSecundario")
        diseno.addWidget(self.etiqueta_contador)
        diseno.addWidget(self.etiqueta_resumen)

        self.boton_unir = QPushButton("Unir archivos PDF")
        self.boton_unir.setObjectName("botonPrincipal")
        self.boton_unir.setToolTip(
            "Crea un único PDF con los documentos seleccionados."
        )
        self.boton_unir.clicked.connect(self.unir_pdf)
        diseno.addWidget(self.boton_unir)

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

        self.actualizar_contador()

    def seleccionar_archivos(self):
        """Selecciona uno o más PDF desde el explorador de Windows."""
        if self.trabajador is not None:
            return
        rutas, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos PDF", "", "Documentos PDF (*.pdf)"
        )
        self.agregar_archivos(rutas)

    def agregar_archivos(self, rutas):
        """Incorpora archivos sin duplicar rutas."""
        if self.trabajador is not None:
            return
        for ruta in rutas:
            archivo = Path(ruta)
            if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
                continue
            ruta_normalizada = str(archivo.resolve())
            if ruta_normalizada in self.rutas_pdf:
                continue
            self.rutas_pdf.append(ruta_normalizada)
            self.lista_archivos.addItem(archivo.name)
        self.actualizar_contador()

    def actualizar_contador(self):
        """Actualiza resumen y alterna entre lista y estado vacío."""
        cantidad = len(self.rutas_pdf)
        self.etiqueta_contador.setText(
            f"{cantidad} archivos seleccionados"
        )
        self.actualizar_resumen_pdf()
        if cantidad == 0:
            self.contenedor_documentos.setCurrentWidget(self.estado_vacio)
        else:
            self.contenedor_documentos.setCurrentWidget(self.lista_archivos)
        self.actualizar_estado_botones()

    def actualizar_resumen_pdf(self):
        """Calcula páginas y tamaño aproximado de los PDF elegidos."""
        total_paginas = 0
        total_bytes = 0
        documentos_sin_lectura = 0
        for ruta in self.rutas_pdf:
            archivo = Path(ruta)
            try:
                total_bytes += archivo.stat().st_size
                with pymupdf.open(archivo) as documento:
                    total_paginas += documento.page_count
            except (OSError, ValueError, RuntimeError):
                documentos_sin_lectura += 1

        total_mb = total_bytes / (1024 * 1024)
        if documentos_sin_lectura:
            texto_paginas = (
                f"{total_paginas} páginas identificadas "
                f"({documentos_sin_lectura} PDF sin leer)"
            )
        else:
            texto_paginas = f"{total_paginas} páginas"
        self.etiqueta_resumen.setText(
            f"{texto_paginas} | {total_mb:.2f} MB"
        )

    def actualizar_estado_botones(self, indice=None):
        """Deshabilita las acciones que aún no pueden ejecutarse."""
        if self.trabajador is not None:
            return
        cantidad = len(self.rutas_pdf)
        posicion = self.lista_archivos.currentRow()
        self.boton_agregar.setEnabled(True)
        self.boton_subir.setEnabled(posicion > 0)
        self.boton_bajar.setEnabled(0 <= posicion < cantidad - 1)
        self.boton_eliminar.setEnabled(0 <= posicion < cantidad)
        self.boton_unir.setEnabled(cantidad >= 2)

    def subir_archivo(self):
        """Sube un documento una posición en la lista."""
        if self.trabajador is not None:
            return
        indice = self.lista_archivos.currentRow()
        if indice <= 0:
            return
        self.rutas_pdf[indice - 1], self.rutas_pdf[indice] = (
            self.rutas_pdf[indice], self.rutas_pdf[indice - 1]
        )
        elemento = self.lista_archivos.takeItem(indice)
        self.lista_archivos.insertItem(indice - 1, elemento)
        self.lista_archivos.setCurrentRow(indice - 1)
        self.actualizar_estado_botones()

    def bajar_archivo(self):
        """Baja un documento una posición en la lista."""
        if self.trabajador is not None:
            return
        indice = self.lista_archivos.currentRow()
        if indice < 0 or indice >= len(self.rutas_pdf) - 1:
            return
        self.rutas_pdf[indice], self.rutas_pdf[indice + 1] = (
            self.rutas_pdf[indice + 1], self.rutas_pdf[indice]
        )
        elemento = self.lista_archivos.takeItem(indice)
        self.lista_archivos.insertItem(indice + 1, elemento)
        self.lista_archivos.setCurrentRow(indice + 1)
        self.actualizar_estado_botones()

    def eliminar_archivo(self):
        """Quita el documento de la lista sin borrar el original."""
        if self.trabajador is not None:
            return
        indice = self.lista_archivos.currentRow()
        if indice < 0:
            return
        self.rutas_pdf.pop(indice)
        elemento = self.lista_archivos.takeItem(indice)
        del elemento
        self.actualizar_contador()

    def unir_pdf(self):
        """Solicita un destino e inicia la unión."""
        if self.trabajador is not None:
            return
        if len(self.rutas_pdf) < 2:
            QMessageBox.warning(
                self,
                "No se puede iniciar la unión",
                "Para combinar documentos necesitas "
                "seleccionar al menos dos archivos PDF.\n\n"
                "Agrega los documentos que faltan "
                "e intenta nuevamente."
            )
            return
        ruta_destino, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF unido", "documento_unido.pdf",
            "Documentos PDF (*.pdf)"
        )
        if not ruta_destino:
            return
        destino = Path(ruta_destino)
        if destino.suffix.lower() != ".pdf":
            destino = Path(str(destino) + ".pdf")
        if destino.exists():
            QMessageBox.warning(
                self, "Archivo existente",
                "El archivo de destino ya existe. Selecciona otro nombre."
            )
            return
        self.iniciar_union(str(destino))

    def iniciar_union(self, ruta_destino):
        """Inicia el trabajador QThread sin modificar el motor de PDF."""
        if self.trabajador is not None:
            return
        self.boton_agregar.setEnabled(False)
        self.boton_subir.setEnabled(False)
        self.boton_bajar.setEnabled(False)
        self.boton_eliminar.setEnabled(False)
        self.boton_unir.setEnabled(False)
        self.lista_archivos.setEnabled(False)
        self.progreso.setVisible(True)
        self.etiqueta_estado.setText("Uniendo los documentos PDF...")

        self.trabajador = TrabajadorUnionPDF(list(self.rutas_pdf), ruta_destino)
        self.trabajador.union_exitosa.connect(self.union_completada)
        self.trabajador.union_fallida.connect(self.union_con_error)
        self.trabajador.finished.connect(self.finalizar_union)
        self.trabajador.start()

    def union_completada(self, ruta):
        """Muestra el aviso de éxito existente."""
        self.etiqueta_estado.setText(
            "Union de PDF completada correctamente."
        )
        QMessageBox.information(
            self,
            "PDF unido correctamente",
            "¡La unión de documentos ha finalizado!\n\n"
            "Todos los archivos seleccionados se han "
            "combinado en un único documento PDF.\n\n"
            f"Ubicación del archivo:\n{ruta}\n\n"
            "Te recomendamos revisar el documento "
            "generado para comprobar su contenido."
        )

    def union_con_error(self, mensaje):
        """Muestra el aviso de error sin ocultar información."""
        self.etiqueta_estado.setText(
            "No se pudo completar la unión de PDF."
        )
        QMessageBox.critical(
            self,
            "No se pudo completar la unión",
            "DocLab encontró un problema al intentar "
            "combinar los documentos seleccionados.\n\n"
            f"Detalle del problema:\n{mensaje}\n\n"
            "Revisa la información anterior "
            "antes de intentarlo nuevamente."
        )

    def finalizar_union(self):
        """Restaura los controles al terminar el trabajador."""
        self.progreso.setVisible(False)
        self.lista_archivos.setEnabled(True)
        self.trabajador = None
        self.actualizar_estado_botones()
