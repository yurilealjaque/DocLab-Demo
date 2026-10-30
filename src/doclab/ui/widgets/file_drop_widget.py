
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ZonaArchivos(QFrame):

    archivo_seleccionado = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("zonaArchivos")
        self.setAcceptDrops(True)
        self.setMinimumHeight(230)

        diseno = QVBoxLayout(self)
        diseno.setSpacing(12)

        titulo = QLabel("Arrastra tu archivo PDF aqui")
        titulo.setObjectName("tituloZona")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        descripcion = QLabel(
            "Tambien puedes seleccionar un archivo desde tu equipo"
        )
        descripcion.setObjectName("textoSecundario")
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)

        boton = QPushButton("Seleccionar PDF")
        boton.setObjectName("botonPrincipal")
        boton.clicked.connect(self.abrir_explorador)

        diseno.addStretch()
        diseno.addWidget(titulo)
        diseno.addWidget(descripcion)
        diseno.addWidget(boton, alignment=Qt.AlignmentFlag.AlignCenter)
        diseno.addStretch()

    def abrir_explorador(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar documento PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        if ruta:
            self.archivo_seleccionado.emit(ruta)

    def dragEnterEvent(self, evento):
        rutas = evento.mimeData().urls()

        if any(
            ruta.isLocalFile()
            and Path(ruta.toLocalFile()).suffix.lower() == ".pdf"
            for ruta in rutas
        ):
            evento.acceptProposedAction()
        else:
            evento.ignore()

    def dropEvent(self, evento):
        for url in evento.mimeData().urls():
            if not url.isLocalFile():
                continue

            ruta = Path(url.toLocalFile())

            if ruta.is_file() and ruta.suffix.lower() == ".pdf":
                self.archivo_seleccionado.emit(str(ruta))
                evento.acceptProposedAction()
                return

        evento.ignore()
