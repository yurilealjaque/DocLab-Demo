
"""
Pantalla de division de archivos PDF.

Permite:
- Seleccionar y validar un PDF.
- Consultar su cantidad de paginas.
- Elegir tres modalidades de division.
- Seleccionar el destino.
- Ejecutar el procesamiento mediante QThread.
- Mostrar resultados y errores.
- Evitar operaciones simultaneas.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QProgressBar,
)

from doclab.document_engine.pdf_validator import validar_pdf
from doclab.workers.pdf_split_worker import TrabajadorDivisionPDF


class PaginaDivisionPDF(QWidget):
    """
    Interfaz para dividir documentos PDF.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ruta_pdf = None
        self.total_paginas = 0
        self.ruta_destino = None
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(32, 32, 32, 32)
        diseno.setSpacing(16)

        # Titulo.
        titulo = QLabel("Dividir PDF")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Extrae paginas o divide un documento "
            "PDF en archivos independientes."
        )
        descripcion.setWordWrap(True)
        descripcion.setObjectName("textoSecundario")

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        # Documento de origen.
        grupo_archivo = QGroupBox("Documento de origen")
        diseno_archivo = QVBoxLayout(grupo_archivo)

        self.etiqueta_archivo = QLabel(
            "No se ha seleccionado ningun archivo."
        )
        self.etiqueta_archivo.setWordWrap(True)

        self.boton_seleccionar = QPushButton(
            "Seleccionar PDF"
        )
        self.boton_seleccionar.clicked.connect(
            self.seleccionar_pdf
        )

        self.etiqueta_paginas = QLabel("Paginas: --")

        diseno_archivo.addWidget(self.etiqueta_archivo)
        diseno_archivo.addWidget(self.boton_seleccionar)
        diseno_archivo.addWidget(self.etiqueta_paginas)

        diseno.addWidget(grupo_archivo)

        # Modalidad.
        grupo_modalidad = QGroupBox(
            "Modalidad de division"
        )
        diseno_modalidad = QVBoxLayout(grupo_modalidad)

        self.selector_modo = QComboBox()
        self.selector_modo.addItem(
            "Extraer un rango de paginas",
            "rango"
        )
        self.selector_modo.addItem(
            "Extraer paginas especificas",
            "paginas"
        )
        self.selector_modo.addItem(
            "Separar todas las paginas",
            "todas"
        )

        self.selector_modo.currentIndexChanged.connect(
            self.actualizar_modo
        )

        diseno_modalidad.addWidget(self.selector_modo)

        # Controles del rango.
        self.grupo_rango = QWidget()
        diseno_rango = QHBoxLayout(self.grupo_rango)
        diseno_rango.setContentsMargins(0, 0, 0, 0)

        self.pagina_inicio = QSpinBox()
        self.pagina_inicio.setRange(1, 1)

        self.pagina_fin = QSpinBox()
        self.pagina_fin.setRange(1, 1)

        diseno_rango.addWidget(QLabel("Desde:"))
        diseno_rango.addWidget(self.pagina_inicio)
        diseno_rango.addWidget(QLabel("Hasta:"))
        diseno_rango.addWidget(self.pagina_fin)

        diseno_modalidad.addWidget(self.grupo_rango)

        # Controles de paginas especificas.
        self.grupo_paginas = QWidget()
        diseno_paginas = QVBoxLayout(self.grupo_paginas)
        diseno_paginas.setContentsMargins(0, 0, 0, 0)

        self.entrada_paginas = QLineEdit()
        self.entrada_paginas.setPlaceholderText(
            "Ejemplo: 1, 3, 5, 8"
        )

        diseno_paginas.addWidget(
            QLabel("Paginas que deseas extraer:")
        )
        diseno_paginas.addWidget(self.entrada_paginas)

        diseno_modalidad.addWidget(self.grupo_paginas)

        self.etiqueta_todas = QLabel(
            "Se generara un PDF independiente "
            "por cada pagina del documento."
        )
        self.etiqueta_todas.setWordWrap(True)

        diseno_modalidad.addWidget(self.etiqueta_todas)
        diseno.addWidget(grupo_modalidad)

        # Destino.
        grupo_destino = QGroupBox(
            "Destino de los archivos"
        )
        diseno_destino = QVBoxLayout(grupo_destino)

        self.etiqueta_destino = QLabel(
            "No se ha seleccionado un destino."
        )
        self.etiqueta_destino.setWordWrap(True)

        self.boton_destino = QPushButton(
            "Seleccionar destino"
        )
        self.boton_destino.clicked.connect(
            self.seleccionar_destino
        )

        diseno_destino.addWidget(self.etiqueta_destino)
        diseno_destino.addWidget(self.boton_destino)

        diseno.addWidget(grupo_destino)

        # Estado del procesamiento.
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 1)
        self.progreso.setValue(0)
        self.progreso.setTextVisible(False)

        self.etiqueta_estado = QLabel(
            "Selecciona un PDF y configura la division."
        )
        self.etiqueta_estado.setWordWrap(True)
        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )

        diseno.addWidget(self.progreso)
        diseno.addWidget(self.etiqueta_estado)

        # Boton principal.
        self.boton_dividir = QPushButton("Dividir PDF")
        self.boton_dividir.clicked.connect(
            self.iniciar_division
        )

        diseno.addWidget(self.boton_dividir)
        diseno.addStretch()

        self.actualizar_modo()
        self.actualizar_boton_dividir()

    def obtener_modo(self):
        return self.selector_modo.currentData()

    def hay_operacion_activa(self):
        """
        Indica si existe una operacion en curso.
        """

        return (
            self.trabajador is not None
            and self.trabajador.isRunning()
        )

    def actualizar_boton_dividir(self):
        """
        Habilita el boton cuando existen
        archivo de origen y destino.
        """

        disponible = (
            self.ruta_pdf is not None
            and self.ruta_destino is not None
            and not self.hay_operacion_activa()
        )

        self.boton_dividir.setEnabled(disponible)

    def actualizar_modo(self, indice=None):
        """
        Muestra los controles correspondientes.
        """

        modo = self.obtener_modo()

        self.grupo_rango.setVisible(modo == "rango")
        self.grupo_paginas.setVisible(modo == "paginas")
        self.etiqueta_todas.setVisible(modo == "todas")

        # Reiniciamos el destino porque las modalidades
        # usan archivos o carpetas de salida distintos.
        self.ruta_destino = None
        self.etiqueta_destino.setText(
            "No se ha seleccionado un destino."
        )

        self.actualizar_boton_dividir()

    def seleccionar_pdf(self):
        """
        Abre el selector de documentos.
        """

        if self.hay_operacion_activa():
            return

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar documento PDF",
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
                "No se pudo abrir el PDF",
                str(error)
            )

    def cargar_pdf(self, ruta):
        """
        Valida el PDF y actualiza la pantalla.
        """

        if self.hay_operacion_activa():
            raise RuntimeError(
                "Hay una division PDF en curso."
            )

        total_paginas = validar_pdf(ruta)

        self.ruta_pdf = str(ruta)
        self.total_paginas = total_paginas

        self.etiqueta_archivo.setText(
            Path(ruta).name
        )
        self.etiqueta_archivo.setToolTip(str(ruta))

        self.etiqueta_paginas.setText(
            f"Paginas: {total_paginas}"
        )

        self.pagina_inicio.setMaximum(total_paginas)
        self.pagina_fin.setMaximum(total_paginas)

        self.pagina_inicio.setValue(1)
        self.pagina_fin.setValue(total_paginas)

        self.etiqueta_estado.setText(
            "Documento cargado correctamente."
        )

        self.actualizar_boton_dividir()

    def seleccionar_destino(self):
        """
        Selecciona archivo o carpeta de destino.
        """

        if self.hay_operacion_activa():
            return

        modo = self.obtener_modo()

        if modo == "todas":
            ruta = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar carpeta de destino"
            )

        else:
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar PDF extraido",
                "",
                "Documentos PDF (*.pdf)"
            )

        if not ruta:
            return

        if modo != "todas":
            if Path(ruta).suffix.lower() != ".pdf":
                ruta += ".pdf"

        self.ruta_destino = str(ruta)
        self.etiqueta_destino.setText(str(ruta))

        self.actualizar_boton_dividir()

    def obtener_paginas_especificas(self):
        """
        Transforma '1, 4, 8' en [1, 4, 8].
        """

        texto = self.entrada_paginas.text().strip()

        if not texto:
            raise ValueError(
                "Debes ingresar al menos una pagina."
            )

        partes = texto.split(",")
        paginas = []

        for parte in partes:
            numero = parte.strip()

            if not numero.isdecimal():
                raise ValueError(
                    "Ingresa numeros separados por comas. "
                    "Ejemplo: 1, 4, 8."
                )

            paginas.append(int(numero))

        if len(paginas) != len(set(paginas)):
            raise ValueError(
                "No se permiten paginas repetidas."
            )

        for numero in paginas:
            if (
                numero < 1
                or numero > self.total_paginas
            ):
                raise ValueError(
                    f"La pagina {numero} esta "
                    "fuera del documento."
                )

        return paginas

    def preparar_solicitud(self):
        """
        Valida los datos de la interfaz.

        Retorna un diccionario con los parametros
        necesarios para crear el trabajador.
        """

        if not self.ruta_pdf:
            raise ValueError(
                "Debes seleccionar un documento PDF."
            )

        if not self.ruta_destino:
            raise ValueError(
                "Debes seleccionar un destino."
            )

        modo = self.obtener_modo()

        solicitud = {
            "modo": modo,
            "ruta_origen": self.ruta_pdf,
            "ruta_destino": self.ruta_destino,
        }

        if modo == "rango":
            inicio = self.pagina_inicio.value()
            fin = self.pagina_fin.value()

            if fin < inicio:
                raise ValueError(
                    "La pagina final no puede ser "
                    "menor que la inicial."
                )

            solicitud["pagina_inicio"] = inicio
            solicitud["pagina_fin"] = fin

        elif modo == "paginas":
            solicitud["paginas"] = (
                self.obtener_paginas_especificas()
            )

        elif modo != "todas":
            raise ValueError(
                "Modalidad de division no valida."
            )

        return solicitud

    def cambiar_estado_procesamiento(self, activo):
        """
        Bloquea controles durante el procesamiento
        y actualiza la barra de actividad.
        """

        self.boton_seleccionar.setEnabled(not activo)
        self.selector_modo.setEnabled(not activo)
        self.pagina_inicio.setEnabled(not activo)
        self.pagina_fin.setEnabled(not activo)
        self.entrada_paginas.setEnabled(not activo)
        self.boton_destino.setEnabled(not activo)

        if activo:
            # Barra indeterminada: no disponemos
            # todavia de progreso por pagina.
            self.progreso.setRange(0, 0)
            self.boton_dividir.setEnabled(False)

            self.etiqueta_estado.setText(
                "Procesando documento PDF..."
            )

        else:
            self.progreso.setRange(0, 1)
            self.progreso.setValue(0)
            self.actualizar_boton_dividir()

    def iniciar_division(self):
        """
        Valida la solicitud e inicia el QThread.
        """

        if self.hay_operacion_activa():
            return

        # Esperar a que el trabajador anterior
        # haya finalizado completamente.
        if self.trabajador is not None:
            return

        try:
            solicitud = self.preparar_solicitud()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Datos invalidos",
                str(error)
            )
            return

        self.trabajador = TrabajadorDivisionPDF(
            **solicitud
        )

        self.trabajador.division_exitosa.connect(
            self.mostrar_resultado
        )

        self.trabajador.division_fallida.connect(
            self.mostrar_error
        )

        self.trabajador.finished.connect(
            self.finalizar_division
        )

        self.cambiar_estado_procesamiento(True)
        self.trabajador.start()

    def mostrar_resultado(self, rutas_generadas):
        """
        Informa cuantos documentos PDF
        fueron generados correctamente.
        """

        cantidad = len(rutas_generadas)

        self.etiqueta_estado.setText(
            f"División completada: "
            f"{cantidad} archivo(s) generado(s)."
        )

        if cantidad == 1:
            descripcion = "Se generó 1 documento PDF."
        else:
            descripcion = (
                f"Se generaron {cantidad} documentos PDF."
            )

        QMessageBox.information(
            self,
            "División completada",
            f"¡La operación finalizó correctamente!\n\n"
            f"{descripcion}\n\n"
            "Te recomendamos revisar los documentos "
            "generados para comprobar su contenido."
        )

    def mostrar_error(self, mensaje):
        """
        Informa un error durante la division PDF.
        """

        self.etiqueta_estado.setText(
            "No se pudo completar la división."
        )

        QMessageBox.critical(
            self,
            "No se pudo completar la división",
            "DocLab encontró un problema al intentar "
            "dividir el documento PDF.\n\n"
            f"Detalle del problema:\n{mensaje}\n\n"
            "Revisa la información anterior "
            "antes de intentarlo nuevamente."
        )

    def finalizar_division(self):
        """
        Restaura los controles una vez
        finalizada la ejecucion del hilo.
        """

        self.trabajador = None
        self.cambiar_estado_procesamiento(False)

    def closeEvent(self, evento):
        """
        Evita cerrar la pantalla durante
        una operacion activa.
        """

        if self.hay_operacion_activa():
            QMessageBox.warning(
                self,
                "Operacion en curso",
                "Espera a que finalice la division "
                "antes de cerrar esta ventana."
            )
            evento.ignore()
            return

        super().closeEvent(evento)
