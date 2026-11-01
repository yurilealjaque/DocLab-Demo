
"""
Pantalla para unir archivos PDF en DocLab.

Funcionalidades:
- Seleccionar multiples documentos PDF.
- Evitar archivos duplicados.
- Ordenar archivos mediante Subir y Bajar.
- Eliminar archivos de la lista.
- Mostrar la cantidad de documentos.
- Unir archivos mediante un trabajador QThread.
- Mostrar el estado y resultado de la operacion.
"""

from pathlib import Path
import pymupdf

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from doclab.workers.pdf_merge_worker import (
    TrabajadorUnionPDF
)


class PaginaUnionPDF(QWidget):
    """
    Pantalla de seleccion, organizacion
    y union de documentos PDF.
    """

    def __init__(self):
        super().__init__()

        self.rutas_pdf = []
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        """
        Construye los componentes visuales
        de la pantalla.
        """

        diseno = QVBoxLayout(self)

        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(18)

        # 1. Titulo y descripcion.
        titulo = QLabel("Unir archivos PDF")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Selecciona dos o mas documentos PDF "
            "para combinarlos en un solo archivo."
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setWordWrap(True)

        # 2. Boton para agregar documentos.
        self.boton_agregar = QPushButton(
            "Agregar archivos PDF"
        )
        self.boton_agregar.setObjectName("botonPrincipal")

        self.boton_agregar.clicked.connect(
            self.seleccionar_archivos
        )

        # 3. Lista de documentos.
        self.lista_archivos = QListWidget()

        # Evita que la lista ocupe toda la pantalla.
        self.lista_archivos.setMaximumHeight(280)

        # 4. Botones de ordenamiento.
        self.boton_subir = QPushButton("Subir")
        self.boton_bajar = QPushButton("Bajar")
        self.boton_eliminar = QPushButton("Eliminar")

        self.boton_subir.clicked.connect(
            self.subir_archivo
        )

        self.boton_bajar.clicked.connect(
            self.bajar_archivo
        )

        self.boton_eliminar.clicked.connect(
            self.eliminar_archivo
        )

        diseno_botones = QHBoxLayout()
        diseno_botones.setSpacing(12)

        diseno_botones.addWidget(self.boton_subir)
        diseno_botones.addWidget(self.boton_bajar)
        diseno_botones.addWidget(self.boton_eliminar)

        # 5. Contador de documentos.
        self.etiqueta_contador = QLabel(
            "0 archivos seleccionados"
        )
        self.etiqueta_contador.setObjectName(
            "textoSecundario"
        )
       # Muestra el total de páginas y el tamaño
        # de los documentos seleccionados.
        self.etiqueta_resumen = QLabel(
            "0 páginas | 0,00 MB"
        )

        self.etiqueta_resumen.setObjectName(
            "textoSecundario"
        )

        # 6. Boton principal de union.
        self.boton_unir = QPushButton(
            "Unir archivos PDF"
        )
        self.boton_unir.setObjectName("botonPrincipal")

        self.boton_unir.clicked.connect(
            self.unir_pdf
        )

        # 7. Barra de actividad.
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.setTextVisible(False)
        self.progreso.setVisible(False)

        # 8. Estado de la operacion.
        self.etiqueta_estado = QLabel("")
        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )
        self.etiqueta_estado.setWordWrap(True)

        # 9. Organizacion de la pantalla.
        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(self.boton_agregar)
        diseno.addWidget(self.lista_archivos)
        diseno.addLayout(diseno_botones)
        diseno.addWidget(self.etiqueta_contador)
        diseno.addWidget(self.etiqueta_resumen)
        diseno.addWidget(self.boton_unir)
        diseno.addWidget(self.progreso)
        diseno.addWidget(self.etiqueta_estado)

        # Mantiene los controles agrupados arriba.
        diseno.addStretch()

    def seleccionar_archivos(self):
        """
        Abre el explorador de Windows para
        seleccionar uno o varios PDF.
        """

        rutas, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos PDF",
            "",
            "Documentos PDF (*.pdf)"
        )

        self.agregar_archivos(rutas)

    def agregar_archivos(self, rutas):
        """
        Agrega documentos PDF existentes,
        evitando seleccionar dos veces
        el mismo archivo.
        """

        for ruta in rutas:
            archivo = Path(ruta)

            if not archivo.is_file():
                continue

            if archivo.suffix.lower() != ".pdf":
                continue

            ruta_normalizada = str(
                archivo.resolve()
            )

            if ruta_normalizada in self.rutas_pdf:
                continue

            self.rutas_pdf.append(
                ruta_normalizada
            )

            self.lista_archivos.addItem(
                archivo.name
            )

        self.actualizar_contador()

    def actualizar_contador(self):
        """
        Actualiza la cantidad de documentos
        seleccionados.
        """

        cantidad = len(self.rutas_pdf)

        self.etiqueta_contador.setText(
            f"{cantidad} archivos seleccionados"
        )

        self.actualizar_resumen_pdf()


    def actualizar_resumen_pdf(self):
        """
        Calcula la cantidad total de páginas
        y el tamaño de los PDF seleccionados.
        """

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

        if documentos_sin_lectura > 0:
            texto_paginas = (
                f"{total_paginas} páginas identificadas "
                f"({documentos_sin_lectura} PDF sin leer)"
            )
        else:
            texto_paginas = f"{total_paginas} páginas"

        self.etiqueta_resumen.setText(
            f"{texto_paginas} | {total_mb:.2f} MB"
        )
    def subir_archivo(self):
        """
        Mueve el documento seleccionado
        una posicion hacia arriba.
        """

        indice = self.lista_archivos.currentRow()

        if indice <= 0:
            return

        self.rutas_pdf[indice - 1], self.rutas_pdf[indice] = (
            self.rutas_pdf[indice],
            self.rutas_pdf[indice - 1]
        )

        elemento = self.lista_archivos.takeItem(
            indice
        )

        self.lista_archivos.insertItem(
            indice - 1,
            elemento
        )

        self.lista_archivos.setCurrentRow(
            indice - 1
        )

    def bajar_archivo(self):
        """
        Mueve el documento seleccionado
        una posicion hacia abajo.
        """

        indice = self.lista_archivos.currentRow()

        if (
            indice < 0
            or indice >= len(self.rutas_pdf) - 1
        ):
            return

        self.rutas_pdf[indice], self.rutas_pdf[indice + 1] = (
            self.rutas_pdf[indice + 1],
            self.rutas_pdf[indice]
        )

        elemento = self.lista_archivos.takeItem(
            indice
        )

        self.lista_archivos.insertItem(
            indice + 1,
            elemento
        )

        self.lista_archivos.setCurrentRow(
            indice + 1
        )

    def eliminar_archivo(self):
        """
        Elimina el archivo seleccionado
        de la lista, pero no del computador.
        """

        indice = self.lista_archivos.currentRow()

        if indice < 0:
            return

        self.rutas_pdf.pop(indice)

        elemento = self.lista_archivos.takeItem(
            indice
        )

        del elemento

        self.actualizar_contador()

    def unir_pdf(self):
        """
        Solicita la ruta de salida e inicia
        la union de los documentos.
        """

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
            self,
            "Guardar PDF unido",
            "documento_unido.pdf",
            "Documentos PDF (*.pdf)"
        )

        if not ruta_destino:
            return

        destino = Path(ruta_destino)

        if destino.suffix.lower() != ".pdf":
            destino = Path(
                str(destino) + ".pdf"
            )

        if destino.exists():
            QMessageBox.warning(
                self,
                "Archivo existente",
                "El archivo de destino ya existe. "
                "Selecciona otro nombre."
            )
            return

        self.iniciar_union(
            str(destino)
        )

    def iniciar_union(self, ruta_destino):
        """
        Inicia el trabajador QThread.
        """

        if self.trabajador is not None:
            return

        # Bloquear los controles durante la union.
        self.boton_agregar.setEnabled(False)
        self.boton_subir.setEnabled(False)
        self.boton_bajar.setEnabled(False)
        self.boton_eliminar.setEnabled(False)
        self.boton_unir.setEnabled(False)
        self.lista_archivos.setEnabled(False)

        self.progreso.setVisible(True)

        self.etiqueta_estado.setText(
            "Uniendo los documentos PDF..."
        )

        self.trabajador = TrabajadorUnionPDF(
            list(self.rutas_pdf),
            ruta_destino
        )

        self.trabajador.union_exitosa.connect(
            self.union_completada
        )

        self.trabajador.union_fallida.connect(
            self.union_con_error
        )

        self.trabajador.finished.connect(
            self.finalizar_union
        )

        self.trabajador.start()

    def union_completada(self, ruta):
        """
        Informa que el PDF se genero
        correctamente.
        """

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
        """
        Muestra un error comprensible al usuario,
        conservando la explicación del trabajador.
        """

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
        """
        Restaura los controles cuando
        termina el trabajador.
        """

        self.progreso.setVisible(False)

        self.boton_agregar.setEnabled(True)
        self.boton_subir.setEnabled(True)
        self.boton_bajar.setEnabled(True)
        self.boton_eliminar.setEnabled(True)
        self.boton_unir.setEnabled(True)
        self.lista_archivos.setEnabled(True)

        self.trabajador = None
