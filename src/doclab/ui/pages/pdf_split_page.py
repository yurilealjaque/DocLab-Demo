
"""
Pantalla de division de archivos PDF.

Funcionalidades:
- Seleccionar y validar un documento PDF.
- Consultar su cantidad de paginas.
- Elegir entre tres modalidades de division.
- Mostrar explicaciones de cada modalidad.
- Seleccionar el destino de los archivos.
- Ejecutar la division mediante QThread.
- Mostrar resultados y errores.
- Evitar operaciones simultaneas.

La interfaz utiliza desplazamiento vertical para
impedir que los controles se compriman o se corten.
"""

from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QPushButton,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QProgressBar,
    QSizePolicy,
)

from doclab.document_engine.pdf_validator import validar_pdf
from doclab.workers.pdf_split_worker import TrabajadorDivisionPDF


class PaginaDivisionPDF(QWidget):
    """
    Interfaz grafica para dividir documentos PDF.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ruta_pdf = None
        self.total_paginas = 0
        self.ruta_destino = None
        self.trabajador = None

        self.crear_interfaz()

    def crear_interfaz(self):
        """
        Construye una interfaz desplazable para
        evitar que los controles se compriman.
        """

        # ---------------------------------------
        # 1. CONTENEDOR PRINCIPAL
        # ---------------------------------------

        diseno_principal = QVBoxLayout(self)

        diseno_principal.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_principal.setSpacing(0)

        # Área de desplazamiento vertical.
        self.area_desplazamiento = QScrollArea()

        self.area_desplazamiento.setWidgetResizable(
            True
        )

        self.area_desplazamiento.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.area_desplazamiento.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # El desplazamiento vertical aparece
        # solamente cuando es necesario.
        self.area_desplazamiento.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Contenedor del contenido desplazable.
        contenedor = QWidget()

        diseno = QVBoxLayout(contenedor)

        diseno.setContentsMargins(
            32, 32, 32, 32
        )

        diseno.setSpacing(16)

        # Evita que Qt comprima los controles
        # por debajo de su tamaño mínimo.
        diseno.setSizeConstraint(
            QLayout.SizeConstraint.SetMinimumSize
        )

        self.area_desplazamiento.setWidget(
            contenedor
        )

        diseno_principal.addWidget(
            self.area_desplazamiento
        )

        # ---------------------------------------
        # 2. TITULO Y DESCRIPCION
        # ---------------------------------------

        titulo = QLabel(
            "Dividir PDF"
        )

        titulo.setObjectName(
            "tituloPagina"
        )

        descripcion = QLabel(
            "Extrae páginas o divide un documento "
            "PDF en archivos independientes."
        )

        descripcion.setWordWrap(True)

        descripcion.setObjectName(
            "textoSecundario"
        )

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        # ---------------------------------------
        # 3. DOCUMENTO DE ORIGEN
        # ---------------------------------------

        grupo_archivo = QGroupBox(
            "Documento de origen"
        )

        diseno_archivo = QVBoxLayout(
            grupo_archivo
        )

        diseno_archivo.setSpacing(10)

        self.etiqueta_archivo = QLabel(
            "No se ha seleccionado ningún archivo."
        )

        self.etiqueta_archivo.setWordWrap(True)

        self.boton_seleccionar = QPushButton(
            "Seleccionar PDF"
        )

        self.boton_seleccionar.clicked.connect(
            self.seleccionar_pdf
        )

        self.etiqueta_paginas = QLabel(
            "Páginas: --"
        )

        diseno_archivo.addWidget(
            self.etiqueta_archivo
        )

        diseno_archivo.addWidget(
            self.boton_seleccionar
        )

        diseno_archivo.addWidget(
            self.etiqueta_paginas
        )

        diseno.addWidget(
            grupo_archivo
        )

        # ---------------------------------------
        # 4. MODALIDAD DE DIVISION
        # ---------------------------------------

        grupo_modalidad = QGroupBox(
            "Modalidad de división"
        )

        diseno_modalidad = QVBoxLayout(
            grupo_modalidad
        )

        diseno_modalidad.setSpacing(12)

        self.selector_modo = QComboBox()

        self.selector_modo.addItem(
            "Extraer un rango de páginas",
            "rango"
        )

        self.selector_modo.addItem(
            "Extraer páginas específicas",
            "paginas"
        )

        self.selector_modo.addItem(
            "Separar todas las páginas",
            "todas"
        )

        self.selector_modo.currentIndexChanged.connect(
            self.actualizar_modo
        )

        diseno_modalidad.addWidget(
            self.selector_modo
        )

        # ---------------------------------------
        # 5. TARJETA INFORMATIVA
        # ---------------------------------------

        self.tarjeta_modo = QFrame()

        self.tarjeta_modo.setObjectName(
            "tarjetaModo"
        )

        self.tarjeta_modo.setStyleSheet(
            """
            QFrame#tarjetaModo {
                background-color: #232230;
                border: 1px solid #514568;
                border-left: 3px solid #A78BFA;
                border-radius: 10px;
            }

            QFrame#tarjetaModo QLabel {
                background-color: transparent;
                border: none;
                color: #DDD7EB;
                font-size: 13px;
            }
            """
        )

        # Garantiza un espacio suficiente
        # para la explicación completa.
        self.tarjeta_modo.setMinimumHeight(145)

        self.tarjeta_modo.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )

        diseno_tarjeta = QVBoxLayout(
            self.tarjeta_modo
        )

        diseno_tarjeta.setContentsMargins(
            18, 14, 18, 14
        )

        diseno_tarjeta.setSpacing(8)

        self.descripcion_modo = QLabel()

        self.descripcion_modo.setWordWrap(True)

        self.descripcion_modo.setAlignment(
            Qt.AlignmentFlag.AlignTop
            | Qt.AlignmentFlag.AlignLeft
        )

        diseno_tarjeta.addWidget(
            self.descripcion_modo
        )

        diseno_modalidad.addWidget(
            self.tarjeta_modo
        )

        # ---------------------------------------
        # 6. CONTROLES DE RANGO
        # ---------------------------------------

        self.grupo_rango = QWidget()

        diseno_rango = QHBoxLayout(
            self.grupo_rango
        )

        diseno_rango.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_rango.setSpacing(8)

        self.pagina_inicio = QSpinBox()
        self.pagina_inicio.setRange(1, 1)

        self.pagina_fin = QSpinBox()
        self.pagina_fin.setRange(1, 1)

        diseno_rango.addWidget(
            QLabel("Desde:")
        )

        diseno_rango.addWidget(
            self.pagina_inicio
        )

        diseno_rango.addWidget(
            QLabel("Hasta:")
        )

        diseno_rango.addWidget(
            self.pagina_fin
        )

        diseno_modalidad.addWidget(
            self.grupo_rango
        )

        # ---------------------------------------
        # 7. PAGINAS ESPECIFICAS
        # ---------------------------------------

        self.grupo_paginas = QWidget()

        diseno_paginas = QVBoxLayout(
            self.grupo_paginas
        )

        diseno_paginas.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_paginas.setSpacing(8)

        self.entrada_paginas = QLineEdit()

        self.entrada_paginas.setPlaceholderText(
            "Ejemplo: 1, 3, 5, 8"
        )

        diseno_paginas.addWidget(
            QLabel("Páginas que deseas extraer:")
        )

        diseno_paginas.addWidget(
            self.entrada_paginas
        )

        diseno_modalidad.addWidget(
            self.grupo_paginas
        )

        # ---------------------------------------
        # 8. SEPARAR TODAS LAS PAGINAS
        # ---------------------------------------

        self.etiqueta_todas = QLabel(
            "Se generará un PDF independiente "
            "por cada página del documento."
        )

        self.etiqueta_todas.setWordWrap(True)

        diseno_modalidad.addWidget(
            self.etiqueta_todas
        )

        diseno.addWidget(
            grupo_modalidad
        )

        # ---------------------------------------
        # 9. DESTINO DE LOS ARCHIVOS
        # ---------------------------------------

        grupo_destino = QGroupBox(
            "Destino de los archivos"
        )

        diseno_destino = QVBoxLayout(
            grupo_destino
        )

        diseno_destino.setSpacing(10)

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

        diseno_destino.addWidget(
            self.etiqueta_destino
        )

        diseno_destino.addWidget(
            self.boton_destino
        )

        diseno.addWidget(
            grupo_destino
        )

        # ---------------------------------------
        # 10. ESTADO DEL PROCESAMIENTO
        # ---------------------------------------

        self.progreso = QProgressBar()

        self.progreso.setRange(0, 1)
        self.progreso.setValue(0)
        self.progreso.setTextVisible(False)

        self.etiqueta_estado = QLabel(
            "Selecciona un PDF y configura la división."
        )

        self.etiqueta_estado.setWordWrap(True)

        self.etiqueta_estado.setObjectName(
            "textoSecundario"
        )

        diseno.addWidget(
            self.progreso
        )

        diseno.addWidget(
            self.etiqueta_estado
        )

        # ---------------------------------------
        # 11. BOTON PRINCIPAL
        # ---------------------------------------

        self.boton_dividir = QPushButton(
            "Dividir PDF"
        )

        self.boton_dividir.setObjectName(
            "botonPrincipal"
        )

        self.boton_dividir.clicked.connect(
            self.iniciar_division
        )

        diseno.addWidget(
            self.boton_dividir
        )

        diseno.addStretch()

        # ---------------------------------------
        # 12. ESTADO INICIAL
        # ---------------------------------------

        self.actualizar_modo()
        self.actualizar_boton_dividir()

    def obtener_modo(self):
        """
        Devuelve la modalidad seleccionada.
        """

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
        Habilita el boton cuando se han
        seleccionado origen y destino.
        """

        disponible = (
            self.ruta_pdf is not None
            and self.ruta_destino is not None
            and not self.hay_operacion_activa()
        )

        self.boton_dividir.setEnabled(
            disponible
        )

    def actualizar_modo(self, indice=None):
        """
        Actualiza la explicacion y los controles
        correspondientes a la modalidad elegida.
        """

        modo = self.obtener_modo()

        # ---------------------------------------
        # EXPLICACIONES DINAMICAS
        # ---------------------------------------

        if modo == "rango":

            self.descripcion_modo.setText(
                "¿Qué hace esta modalidad?\n\n"
                "Extrae todas las páginas comprendidas "
                "entre un número inicial y uno final, "
                "incluyendo ambos.\n\n"
                "Ejemplo: desde la página 3 hasta la 8 "
                "se generará un PDF con esas seis páginas."
            )

        elif modo == "paginas":

            self.descripcion_modo.setText(
                "¿Qué hace esta modalidad?\n\n"
                "Permite seleccionar páginas concretas "
                "para reunirlas en un único documento PDF.\n\n"
                "Ejemplo: escribe 1, 3, 5, 8 "
                "para extraer esas cuatro páginas."
            )

        elif modo == "todas":

            self.descripcion_modo.setText(
                "¿Qué hace esta modalidad?\n\n"
                "Crea un archivo PDF independiente "
                "por cada página del documento original.\n\n"
                "Ejemplo: un PDF de 10 páginas generará "
                "10 archivos en la carpeta seleccionada."
            )

        # ---------------------------------------
        # VISIBILIDAD DE LOS CONTROLES
        # ---------------------------------------

        self.grupo_rango.setVisible(
            modo == "rango"
        )

        self.grupo_paginas.setVisible(
            modo == "paginas"
        )

        self.etiqueta_todas.setVisible(
            modo == "todas"
        )

        # Al cambiar de modalidad se reinicia
        # el destino porque puede variar
        # entre archivo PDF y carpeta.
        self.ruta_destino = None

        self.etiqueta_destino.setText(
            "No se ha seleccionado un destino."
        )

        self.actualizar_boton_dividir()

    def seleccionar_pdf(self):
        """
        Abre el selector de archivos PDF.
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
        Valida el PDF y actualiza la interfaz.
        """

        if self.hay_operacion_activa():

            raise RuntimeError(
                "Hay una división PDF en curso."
            )

        total_paginas = validar_pdf(ruta)

        self.ruta_pdf = str(ruta)
        self.total_paginas = total_paginas

        self.etiqueta_archivo.setText(
            Path(ruta).name
        )

        self.etiqueta_archivo.setToolTip(
            str(ruta)
        )

        self.etiqueta_paginas.setText(
            f"Páginas: {total_paginas}"
        )

        self.pagina_inicio.setMaximum(
            total_paginas
        )

        self.pagina_fin.setMaximum(
            total_paginas
        )

        self.pagina_inicio.setValue(1)

        self.pagina_fin.setValue(
            total_paginas
        )

        self.etiqueta_estado.setText(
            "Documento cargado correctamente."
        )

        self.actualizar_boton_dividir()

    def seleccionar_destino(self):
        """
        Selecciona archivo o carpeta
        segun la modalidad.
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
                "Guardar PDF extraído",
                "",
                "Documentos PDF (*.pdf)"
            )

        if not ruta:
            return

        if modo != "todas":

            if Path(ruta).suffix.lower() != ".pdf":
                ruta += ".pdf"

        self.ruta_destino = str(ruta)

        self.etiqueta_destino.setText(
            str(ruta)
        )

        self.actualizar_boton_dividir()

    def obtener_paginas_especificas(self):
        """
        Convierte '1, 4, 8' en [1, 4, 8].
        """

        texto = self.entrada_paginas.text().strip()

        if not texto:

            raise ValueError(
                "Debes ingresar al menos una página."
            )

        partes = texto.split(",")
        paginas = []

        for parte in partes:

            numero = parte.strip()

            if not numero.isdecimal():

                raise ValueError(
                    "Ingresa números separados por comas. "
                    "Ejemplo: 1, 4, 8."
                )

            paginas.append(
                int(numero)
            )

        if len(paginas) != len(set(paginas)):

            raise ValueError(
                "No se permiten páginas repetidas."
            )

        for numero in paginas:

            if (
                numero < 1
                or numero > self.total_paginas
            ):

                raise ValueError(
                    f"La página {numero} está "
                    "fuera del documento."
                )

        return paginas

    def preparar_solicitud(self):
        """
        Valida los datos y prepara
        los parametros de la division.
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
                    "La página final no puede ser "
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
                "Modalidad de división no válida."
            )

        return solicitud

    def cambiar_estado_procesamiento(self, activo):
        """
        Bloquea controles durante la division
        y actualiza la barra de actividad.
        """

        self.boton_seleccionar.setEnabled(
            not activo
        )

        self.selector_modo.setEnabled(
            not activo
        )

        self.pagina_inicio.setEnabled(
            not activo
        )

        self.pagina_fin.setEnabled(
            not activo
        )

        self.entrada_paginas.setEnabled(
            not activo
        )

        self.boton_destino.setEnabled(
            not activo
        )

        if activo:

            # Progreso indeterminado.
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
        Valida la solicitud y ejecuta
        el trabajador en segundo plano.
        """

        if self.hay_operacion_activa():
            return

        if self.trabajador is not None:
            return

        try:

            solicitud = self.preparar_solicitud()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Datos inválidos",
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
        Comunica el resultado de la division.
        """

        cantidad = len(rutas_generadas)

        self.etiqueta_estado.setText(
            f"División completada: "
            f"{cantidad} archivo(s) generado(s)."
        )

        if cantidad == 1:

            descripcion = (
                "Se generó 1 documento PDF."
            )

        else:

            descripcion = (
                f"Se generaron {cantidad} documentos PDF."
            )

        QMessageBox.information(
            self,
            "División completada",
            "¡La operación finalizó correctamente!\n\n"
            f"{descripcion}\n\n"
            "Te recomendamos revisar los documentos "
            "generados para comprobar su contenido."
        )

    def mostrar_error(self, mensaje):
        """
        Informa los errores de division.
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
        finalizada la ejecucion del trabajador.
        """

        self.trabajador = None

        self.cambiar_estado_procesamiento(False)

    def closeEvent(self, evento):
        """
        Evita cerrar la pantalla durante
        una division activa.
        """

        if self.hay_operacion_activa():

            QMessageBox.warning(
                self,
                "Operación en curso",
                "Espera a que finalice la división "
                "antes de cerrar esta ventana."
            )

            evento.ignore()
            return

        super().closeEvent(evento)
