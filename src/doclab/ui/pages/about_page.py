
"""
Pantalla Sobre mí de DocLab.

Responsabilidades:
- Presentar al creador del proyecto.
- Explicar la finalidad educativa de DocLab.
- Mostrar las tecnologías utilizadas.
- Informar el estado actual del proyecto.

Esta pantalla no modifica documentos ni ejecuta
operaciones en segundo plano.
"""

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class PaginaSobreMi(QWidget):
    """
    Pantalla informativa sobre el creador
    y el propósito educativo de DocLab.
    """

    def __init__(self):
        super().__init__()

        self.crear_interfaz()

    def crear_etiqueta(self, texto, identificador=None):
        """
        Crea una etiqueta adaptable.

        Parámetros:
        - texto: contenido que se mostrará.
        - identificador: nombre opcional para
          aplicar los estilos del archivo QSS.
        """

        etiqueta = QLabel(texto)

        etiqueta.setWordWrap(True)

        if identificador is not None:
            etiqueta.setObjectName(identificador)

        return etiqueta

    def crear_tarjeta(self):
        """
        Crea una tarjeta reutilizando
        los estilos existentes de DocLab.
        """

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "tarjetaHerramienta"
        )

        contenido = QVBoxLayout(tarjeta)

        contenido.setContentsMargins(
            24, 24, 24, 24
        )

        contenido.setSpacing(14)

        return tarjeta, contenido

    def crear_interfaz(self):
        """
        Construye la interfaz completa
        de la pantalla Sobre mí.
        """

        # ---------------------------------------
        # 1. CONTENEDOR PRINCIPAL
        # ---------------------------------------

        diseno_principal = QVBoxLayout(self)

        diseno_principal.setContentsMargins(
            0, 0, 0, 0
        )

        diseno_principal.setSpacing(0)

        desplazamiento = QScrollArea()

        desplazamiento.setWidgetResizable(True)

        desplazamiento.setFrameShape(
            QFrame.Shape.NoFrame
        )

        contenedor = QWidget()

        diseno = QVBoxLayout(contenedor)

        diseno.setContentsMargins(
            32, 32, 32, 32
        )

        diseno.setSpacing(18)

        # ---------------------------------------
        # 2. ENCABEZADO
        # ---------------------------------------

        titulo = self.crear_etiqueta(
            "Sobre mí",
            "tituloPagina"
        )

        descripcion = self.crear_etiqueta(
            "Conoce al creador de DocLab y "
            "el propósito de este proyecto.",
            "textoSecundario"
        )

        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)

        # ---------------------------------------
        # 3. TARJETA DEL CREADOR
        # ---------------------------------------

        tarjeta_autor, contenido_autor = (
            self.crear_tarjeta()
        )

        nombre = self.crear_etiqueta(
            "Yuri Ignacio Leal Jaque",
            "subtituloPagina"
        )

        rol = self.crear_etiqueta(
            "Creador y desarrollador de DocLab",
            "textoSecundario"
        )

        contenido_autor.addWidget(nombre)
        contenido_autor.addWidget(rol)

        diseno.addWidget(tarjeta_autor)

        # ---------------------------------------
        # 4. ORIGEN Y OBJETIVO DEL PROYECTO
        # ---------------------------------------

        tarjeta_proyecto, contenido_proyecto = (
            self.crear_tarjeta()
        )

        subtitulo_proyecto = self.crear_etiqueta(
            "¿Por qué nació DocLab?",
            "subtituloPagina"
        )

        descripcion_proyecto = self.crear_etiqueta(
            "DocLab nace como un proyecto personal "
            "desarrollado con fines educativos y "
            "de práctica, cuyo objetivo es adquirir "
            "experiencia, fortalecer conocimientos "
            "y desarrollar competencias en "
            "programación e ingeniería de software."
        )

        descripcion_aprendizaje = self.crear_etiqueta(
            "A través de su construcción, busco "
            "aplicar conceptos de arquitectura "
            "modular, desarrollo de interfaces "
            "gráficas, procesamiento documental, "
            "automatización de pruebas y buenas "
            "prácticas de programación."
        )

        descripcion_evolucion = self.crear_etiqueta(
            "El proyecto evoluciona de manera "
            "incremental mediante el aprendizaje "
            "continuo, la experimentación y la "
            "resolución de problemas reales."
        )

        contenido_proyecto.addWidget(
            subtitulo_proyecto
        )

        contenido_proyecto.addWidget(
            descripcion_proyecto
        )

        contenido_proyecto.addWidget(
            descripcion_aprendizaje
        )

        contenido_proyecto.addWidget(
            descripcion_evolucion
        )

        diseno.addWidget(tarjeta_proyecto)

        # ---------------------------------------
# 5. TECNOLOGÍAS UTILIZADAS
# ---------------------------------------

        tarjeta_tecnologias, contenido_tecnologias = (
            self.crear_tarjeta()
        )

        titulo_tecnologias = self.crear_etiqueta(
            "Tecnologías y aprendizaje",
            "subtituloPagina"
        )

        tecnologias = self.crear_etiqueta(
            "Python · PySide6 · PyMuPDF · "
            "Procesamiento OCR · pytest · "
            "Git y GitHub"
        )

        asistencia = self.crear_etiqueta(
    "Durante el desarrollo se han utilizado "
    "diversos recursos de aprendizaje, como "
    "foros, videos, herramientas de inteligencia "
    "artificial, bibliografía y documentación "
    "técnica, como apoyo educativo para adquirir "
    "conocimientos y experiencia.",
    "textoSecundario"
)

        contenido_tecnologias.addWidget(
            titulo_tecnologias
        )

        contenido_tecnologias.addWidget(
            tecnologias
        )

        contenido_tecnologias.addWidget(
            asistencia
        )

        diseno.addWidget(tarjeta_tecnologias)
        # ---------------------------------------
        # 6. FINALIDAD ACTUAL DEL PROYECTO
        # ---------------------------------------

        tarjeta_finalidad, contenido_finalidad = (
            self.crear_tarjeta()
        )

        titulo_finalidad = self.crear_etiqueta(
            "Finalidad de DocLab",
            "subtituloPagina"
        )

        finalidad = self.crear_etiqueta(
            "DocLab es un proyecto personal en "
            "desarrollo con el fin de ayudar a "
            "las personas. En el presente, "
            "es un proyecto solo educativo."
        )

        finalidad.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        contenido_finalidad.addWidget(
            titulo_finalidad
        )

        contenido_finalidad.addWidget(
            finalidad
        )

        diseno.addWidget(tarjeta_finalidad)

        # ---------------------------------------
        # 7. AJUSTES FINALES
        # ---------------------------------------

        diseno.addStretch()

        desplazamiento.setWidget(
            contenedor
        )

        diseno_principal.addWidget(
            desplazamiento
        )
