
"""
Servicio de conversion PDF a Word con OCR.

Coordina los componentes existentes de DocLab.

Este servicio no modifica la conversion
tradicional mediante pdf2docx.
"""

from dataclasses import dataclass
from pathlib import Path

from doclab.document_engine.ocr_unified import (
    procesar_ocr_unificado
)

from doclab.document_engine.pdf_layout import (
    analizar_estructura_pdf
)

from doclab.document_engine.pdf_image_extractor import (
    extraer_imagenes_pdf
)

from doclab.document_engine.word_positioned_plan import (
    crear_plan_word_posicionado
)

from doclab.document_engine.word_layout_export import (
    exportar_plan_a_word
)


@dataclass(frozen=True)
class ResultadoConversionOCR:
    ruta_destino: str
    total_paginas: int
    paginas_con_ocr: int
    imagenes_exportadas: int


class ServicioConversionOCR:
    """
    Servicio de alto nivel para convertir PDF a DOCX
    utilizando reconocimiento OCR cuando corresponde.
    """

    def convertir(
        self,
        origen,
        destino,
        idioma="spa+eng",
        dpi=300,
        carpeta_tessdata=None
    ):
        """
        Ejecuta el flujo completo de conversion OCR.

        Retorna un ResultadoConversionOCR.
        """

        ruta_origen = Path(origen)
        ruta_destino = Path(destino)

        # 1. Reconocer texto y recuperar coordenadas.
        resultado_unificado = procesar_ocr_unificado(
            ruta_archivo=ruta_origen,
            idioma=idioma,
            dpi=dpi,
            carpeta_tessdata=carpeta_tessdata
        )

        # 2. Analizar la estructura del documento.
        resultado_estructura = analizar_estructura_pdf(
            ruta_origen
        )

        # 3. Extraer las imagenes originales.
        resultado_imagenes = extraer_imagenes_pdf(
            ruta_origen
        )

        # 4. Construir el plan de reconstruccion.
        resultado_plan = crear_plan_word_posicionado(
            resultado_ocr=resultado_unificado.documento,
            resultado_estructura=resultado_estructura,
            resultados_posicionados=(
                resultado_unificado.paginas_posicionadas
            )
        )

        # 5. Generar el documento Word final.
        ruta_generada = exportar_plan_a_word(
            resultado_plan=resultado_plan,
            resultado_imagenes=resultado_imagenes,
            ruta_destino=ruta_destino
        )

        # 6. Calcular estadisticas del procesamiento.
        paginas_con_ocr = sum(
            pagina.metodo in (
                "ocr_parcial",
                "ocr_completo"
            )
            for pagina in resultado_unificado.documento.paginas
        )

        imagenes_exportadas = sum(
            elemento.tipo == "imagen"
            for elemento in resultado_plan.elementos
        )

        # 7. Entregar el resultado al consumidor.
        return ResultadoConversionOCR(
            ruta_destino=str(ruta_generada),
            total_paginas=(
                resultado_unificado.documento.total_paginas
            ),
            paginas_con_ocr=paginas_con_ocr,
            imagenes_exportadas=imagenes_exportadas
        )
