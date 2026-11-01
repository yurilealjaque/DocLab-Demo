# DocLab

**Aplicación de escritorio para convertir y gestionar documentos, desarrollada con Python y PySide6.**

DocLab es un proyecto de software modular que busca reunir en una única interfaz herramientas para trabajar con documentos. Su primera funcionalidad es la **conversión de archivos PDF a Word (`.docx`)**. El objetivo a largo plazo es incorporar edición y organización de PDF, OCR, procesamiento por lotes y herramientas de inspección de calidad.

> **Estado del proyecto:** prototipo funcional en desarrollo (versión inicial 0.1.0). La conversión PDF → Word fue probada manualmente con éxito. Todavía no contamos con una batería de pruebas automatizadas ni con garantías de conservación exacta del diseño original.

## Funcionalidades actuales

- **Conversión PDF a Word:** genera documentos `.docx` editables a partir de PDF compatibles.
- **Selección de archivos:** permite elegir un PDF mediante el explorador de archivos de Windows.
- **Arrastrar y soltar:** admite soltar un archivo PDF en la zona correspondiente de la interfaz.
- **Selección de destino:** permite indicar dónde guardar el archivo Word.
- **Interfaz gráfica:** incluye menú lateral, pantalla de inicio y pantalla de conversión.
- **Procesamiento en segundo plano:** la conversión se ejecuta mediante `QThread` para mantener receptiva la interfaz.
- **Indicador de actividad:** muestra una barra de progreso indeterminado mientras se ejecuta la operación.
- **Mensajes de resultado:** informa al usuario si la conversión finaliza o produce un error.
- **Protección básica contra sobrescritura:** comprueba si el archivo de destino ya existe.

Las opciones de unir PDF, comprimir PDF, OCR e historial aparecen como funcionalidades futuras y **aún no están implementadas**.

## Tecnologías utilizadas

| Tecnología | Función |
| --- | --- |
| Python 3.13 | Lenguaje principal |
| PySide6 (Qt for Python) | Interfaz gráfica de escritorio |
| Qt Widgets | Ventanas, botones, paneles y navegación |
| QSS (Qt Style Sheets) | Estilos visuales, colores y tema oscuro |
| pdf2docx | Conversión de PDF a Word |
| QThread y Signal | Ejecución en segundo plano y comunicación con la interfaz |
| pathlib | Validación y manejo de rutas de archivos |
| setuptools / pyproject.toml | Configuración e instalación editable del paquete |
| Git y GitHub | Control de versiones y publicación del código |

**Nota técnica:** `pdf2docx` tiene limitaciones con PDF escaneados, tablas complejas y diseños elaborados. El resultado debe revisarse antes de utilizarlo como copia fiel del original. La biblioteca también tiene mantenimiento limitado; por eso la integración está aislada en el motor documental y podrá sustituirse en versiones futuras.

## Estructura del proyecto

```text
DocLab/
├── src/
│   └── doclab/
│       ├── __init__.py
│       ├── main.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── pages/
│       │   │   ├── __init__.py
│       │   │   ├── home_page.py
│       │   │   └── converter_page.py
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   └── file_drop_widget.py
│       │   └── styles/
│       │       ├── __init__.py
│       │       └── theme.qss
│       ├── services/
│       │   ├── __init__.py
│       │   └── conversion_service.py
│       ├── document_engine/
│       │   ├── __init__.py
│       │   └── pdf_to_word.py
│       └── workers/
│           ├── __init__.py
│           └── conversion_worker.py
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

> Esta estructura representa la versión que hemos diseñado. Si todavía no se incorporó alguno de los módulos visuales en el repositorio, la estructura debe ajustarse para reflejar el código efectivamente publicado.

## Arquitectura y explicación del código

El proyecto sigue una **organización modular por responsabilidades**: la interfaz recibe eventos del usuario, un servicio coordina la solicitud, un motor ejecuta la transformación y un trabajador maneja la tarea fuera del hilo gráfico.

### `src/doclab/main.py` — Punto de entrada

- Crea la instancia de `QApplication`, necesaria para ejecutar una aplicación gráfica Qt.
- Carga los estilos desde `ui/styles/theme.qss`.
- Crea y muestra `VentanaPrincipal`.
- Inicia el bucle de eventos con `aplicacion.exec()`.

### `src/doclab/ui/main_window.py` — Ventana y navegación

- Define la clase `VentanaPrincipal`, que hereda de `QMainWindow`.
- Construye el menú lateral y el contenedor de pantallas.
- Utiliza `QStackedWidget` para alternar entre Inicio y Convertir sin abrir ventanas independientes.
- Recibe la ruta de un PDF seleccionado en Inicio y la envía a la pantalla del conversor.

### `src/doclab/ui/pages/home_page.py` — Pantalla de inicio

- Presenta DocLab y sus herramientas.
- Instancia el componente `ZonaArchivos`.
- Construye tarjetas de funcionalidades mediante `QGridLayout`.
- Emite señales para navegar al conversor o trasladar una ruta de archivo seleccionada.
- Mantiene deshabilitadas las herramientas que aún no están implementadas.

### `src/doclab/ui/widgets/file_drop_widget.py` — Selector de PDF

- Define `ZonaArchivos`, un componente reutilizable basado en `QFrame`.
- Permite elegir un PDF con `QFileDialog`.
- Implementa `dragEnterEvent()` y `dropEvent()` para aceptar archivos locales con extensión `.pdf`.
- Emite `archivo_seleccionado = Signal(str)` para informar la ruta, sin ejecutar la conversión por su cuenta.

### `src/doclab/ui/pages/converter_page.py` — Pantalla del conversor

- Valida que el PDF seleccionado exista y tenga la extensión esperada.
- Permite escoger la ruta de salida del `.docx`.
- Comprueba si la ruta destino ya está ocupada.
- Crea e inicia un `TrabajadorConversion`.
- Deshabilita los controles pertinentes durante el proceso.
- Muestra un `QProgressBar` indeterminado, y mensajes de éxito o error.

### `src/doclab/workers/conversion_worker.py` — Trabajo en segundo plano

- Declara `TrabajadorConversion`, que hereda de `QThread`.
- Ejecuta el servicio de conversión dentro de `run()`.
- Emite `conversion_exitosa` cuando obtiene la ruta del documento generado.
- Emite `conversion_fallida` cuando captura una excepción.
- Permite que la pantalla principal continúe respondiendo durante la conversión.

### `src/doclab/services/conversion_service.py` — Coordinación

- Expone `ServicioConversion` como intermediario entre la interfaz y el motor documental.
- Por ahora delega la tarea al conversor PDF a Word.
- Está preparado para incorporar validaciones adicionales, alternativas de conversión o procesamiento por lotes sin depender de Qt Widgets.

### `src/doclab/document_engine/pdf_to_word.py` — Motor documental

- Implementa `convertir_pdf_a_word(ruta_origen, ruta_destino)`.
- Utiliza `pathlib.Path` para trabajar con las rutas.
- Verifica existencia y extensión del archivo de entrada y formato de salida.
- Evita sobrescribir un archivo existente.
- Usa `pdf2docx.Converter` para generar el documento `.docx`.
- Comprueba que se haya creado un archivo no vacío.
- Cierra el conversor en un bloque `finally` para liberar recursos incluso si ocurre un error.

**Importante:** que exista un `.docx` no garantiza que toda la estructura visual del PDF se haya conservado. La inspección de contenido y formato está prevista para una fase posterior.

### `src/doclab/ui/styles/theme.qss` — Estilos

- Centraliza el aspecto de la aplicación, incluidas la barra lateral, las tarjetas, los botones y los títulos.
- Aplica una estética oscura con acentos turquesa.
- Evita definir colores y estilos repetidos en múltiples archivos Python.

## Flujo de funcionamiento

```text
Usuario selecciona o arrastra un PDF
              |
              v
      ZonaArchivos (UI)
              |
              v
       PaginaConversor
     (elige destino .docx)
              |
              v
     TrabajadorConversion
             QThread
              |
              v
      ServicioConversion
              |
              v
       convertir_pdf_a_word()
              |
              v
          pdf2docx
              |
              v
       Archivo Word .docx
              |
              v
  Señal de éxito o error a la UI
```

Esta separación permite cambiar el motor de conversión o rediseñar la pantalla sin tener que reescribir toda la aplicación.

## Instalación y ejecución

### Requisitos

- Python 3.13.
- Git (para clonar el repositorio).
- Windows para los comandos de activación que se indican a continuación. La interfaz es de Qt, pero el funcionamiento en otros sistemas todavía no se ha validado.

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/DocLab.git
cd DocLab
```

Sustituye `TU_USUARIO` por el usuario real del repositorio.

### 2. Crear y activar el entorno virtual

En Git Bash (Windows):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Instalar dependencias y el proyecto

```bash
python -m pip install -e .
```

Este comando lee `pyproject.toml` e instala DocLab en modo editable junto con sus dependencias.

### 4. Ejecutar la aplicación

```bash
doclab
```

Como alternativa:

```bash
python -m doclab.main
```

## Cómo convertir un PDF a Word

1. Abre DocLab.
2. Accede a **Convertir** o selecciona un PDF desde la pantalla de inicio.
3. Selecciona o arrastra un archivo `.pdf`.
4. Presiona **Convertir a Word**.
5. Escoge la carpeta y el nombre del documento `.docx` de salida.
6. Espera a que termine el proceso y revisa el mensaje de resultado.
7. Abre el documento generado y verifica que el texto y la presentación sean adecuados.

## Limitaciones conocidas

- Los PDF escaneados pueden requerir OCR, función todavía pendiente.
- Tablas, columnas, imágenes y diseños complejos pueden perder fidelidad durante la conversión.
- El indicador de actividad no muestra porcentaje real.
- No se ha implementado cancelación segura de conversiones ni cierre controlado mientras un trabajador sigue activo.
- El sistema no genera todavía un informe automático de diferencias entre el PDF original y el Word.
- El tratamiento de archivos temporales, limpieza de salidas incompletas y manejo avanzado de errores está pendiente.
- La funcionalidad fue verificada manualmente; todavía faltan pruebas automatizadas y ensayos con archivos variados.

## Próximas etapas (roadmap)

- [x] Diseñar la arquitectura modular del proyecto.
- [x] Crear una interfaz gráfica básica con PySide6.
- [x] Implementar selección y arrastre de archivos PDF.
- [x] Implementar conversión PDF → Word.
- [x] Ejecutar conversiones con `QThread`.
- [x] Comprobar manualmente la generación de un Word editable.
- [ ] Crear pruebas automatizadas con `pytest`.
- [ ] Mejorar el manejo de errores y los registros (`logging`).
- [ ] Incorporar archivos temporales y limpieza ante fallos.
- [ ] Gestionar cancelación y cierre seguro durante conversiones.
- [ ] Añadir conversión por lotes.
- [ ] Incorporar OCR para documentos escaneados.
- [ ] Unir, dividir y comprimir archivos PDF.
- [ ] Crear un inspector de fidelidad de conversión.
- [ ] Implementar historial local de operaciones.
- [ ] Evaluar herramientas de análisis documental e IA local.

## Privacidad

Las operaciones de conversión de esta versión se realizan en el computador del usuario mediante bibliotecas locales. DocLab no incorpora por ahora un servicio propio para subir documentos a la nube.

## Contribución y estado del desarrollo

DocLab es un proyecto de aprendizaje y desarrollo incremental. Su estructura busca facilitar la extensión de funcionalidades, la escritura de pruebas y el mantenimiento del código. Las funcionalidades futuras descritas aquí son objetivos de desarrollo, no capacidades ya disponibles.

---

**DocLab — Convierte, organiza y transforma tus documentos.**


# DocLab avances de proyecto

**Laboratorio documental de escritorio desarrollado en Python y PySide6.**

DocLab es una aplicación de escritorio orientada a la conversión y gestión de documentos. Su primera funcionalidad es convertir archivos **PDF a Word (`.docx`)**, mediante una interfaz gráfica moderna, con procesamiento en segundo plano y un motor de conversión separado de la presentación.

El proyecto se desarrolla de forma incremental, priorizando la mantenibilidad del código, la protección de archivos y las pruebas automatizadas. La visión a largo plazo es integrar herramientas para unir y dividir PDF, compresión, OCR, comparación de documentos y análisis documental.

> **Estado del proyecto:** versión inicial en desarrollo. Conversión PDF → DOCX implementada y probada; 13 pruebas automatizadas aprobadas según la última ejecución comunicada. Algunas funciones descritas como futuras todavía no están disponibles.

## Características implementadas

### Interfaz gráfica

- Interfaz de escritorio desarrollada con **PySide6 (Qt for Python)**.
- Pantalla de inicio y vista dedicada a la conversión de PDF a Word.
- Menú lateral de navegación y estilo oscuro personalizable mediante **QSS**.
- Selección de documentos desde el explorador del sistema y zona de arrastrar y soltar archivos PDF.
- Selección de la ruta de destino para guardar el documento Word.
- Barra de actividad indeterminada mientras se realiza la conversión.
- Mensajes de éxito y error para informar sobre el resultado del proceso.
- Opciones de herramientas futuras visibles como funciones aún no disponibles.

### Conversión PDF a Word

- Conversión de documentos PDF a archivos **`.docx`** mediante la biblioteca `pdf2docx`.
- Separación entre interfaz, servicio de conversión y motor documental.
- Ejecución en un hilo de trabajo con **`QThread`** para evitar bloquear la interfaz durante tareas prolongadas.
- Validaciones de existencia de archivos, extensión de origen y destino, carpeta de salida y protección contra sobrescrituras.
- Escritura inicial en un archivo temporal, validación estructural del DOCX generado y publicación final por enlace físico mediante `os.link()`.
- Limpieza de archivos temporales ante la finalización normal o las excepciones controladas.

**Limitaciones:** la conversión no garantiza fidelidad visual absoluta en documentos complejos. La publicación por `os.link()` depende de que el sistema de archivos de destino admita enlaces físicos; no existe una copia alternativa automática. La resistencia ante apagones, cierres forzosos y fallas del sistema operativo no es absoluta.

### Validación de archivos PDF

El módulo `pdf_validator.py` realiza comprobaciones previas al procesamiento:

- Verifica que exista el archivo y tenga extensión `.pdf`.
- Intenta abrirlo como PDF mediante **PyMuPDF**.
- Detecta documentos que requieren contraseña, utilizando `needs_pass`.
- Rechaza documentos sin páginas.
- Intenta cargar todas las páginas para identificar ciertos problemas de lectura.
- Distingue excepciones propias: `PDFProtegidoError` y `PDFCorruptoError`.

El servicio `conversion_service.py` integra este validador antes de llamar al motor de conversión. El trabajador contempla mensajes diferenciados para PDF protegidos o corruptos. **La validación no implica detección exhaustiva de toda corrupción posible y el recorrido completo desde la interfaz aún requiere verificación manual específica.**

### Registro y control de ejecución

- Sistema de registros con `logging` y `RotatingFileHandler`.
- Registro de inicio, finalización y tipo de error de las conversiones.
- Archivos rotativos de hasta aproximadamente 1 MB, con tres copias de respaldo configuradas.
- Carpeta local de registros: `~/.doclab/logs/doclab.log`.
- Evita registrar automáticamente los nombres o rutas completas de documentos en los mensajes diseñados para el trabajador.
- La ventana principal contempla `closeEvent()` para impedir el cierre normal de la aplicación mientras una conversión continúa ejecutándose.

> La protección de cierre normal no equivale a cancelación segura ni evita la terminación forzosa de procesos.

## Tecnologías principales

| Tecnología | Propósito |
| --- | --- |
| Python 3.13 | Lenguaje principal de la aplicación |
| PySide6 / Qt Widgets | Interfaz gráfica de escritorio |
| QSS | Estilos visuales |
| `pdf2docx` | Motor inicial de conversión PDF → DOCX |
| PyMuPDF (`pymupdf`) | Apertura, lectura, validación y creación de PDF de prueba |
| `zipfile` | Inspección estructural básica del contenedor DOCX |
| `QThread` y señales Qt | Trabajo en segundo plano y notificación de resultados |
| `logging` | Diagnóstico y registro de eventos |
| `pytest` | Pruebas automatizadas |
| `python-docx` | Lectura del contenido Word en pruebas de integración |
| `setuptools` / `pyproject.toml` | Configuración e instalación editable del proyecto |
| Git y GitHub | Control de versiones |

> `pdf2docx` es una dependencia del prototipo inicial y su mantenimiento futuro deberá evaluarse antes de distribuir el software ampliamente.

## Organización del proyecto

La estructura modular desarrollada hasta ahora sigue esta disposición aproximada:

```text
DocLab/
├── src/
│   └── doclab/
│       ├── __init__.py
│       ├── main.py
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── pages/
│       │   │   ├── home_page.py
│       │   │   └── converter_page.py
│       │   ├── widgets/
│       │   │   └── file_drop_widget.py
│       │   └── styles/
│       │       └── theme.qss
│       ├── services/
│       │   └── conversion_service.py
│       ├── document_engine/
│       │   ├── pdf_to_word.py
│       │   └── pdf_validator.py
│       ├── workers/
│       │   └── conversion_worker.py
│       └── infrastructure/
│           └── logger.py
├── tests/
│   ├── test_pdf_to_word.py
│   ├── test_pdf_validator.py
│   └── test_integracion_pdf.py
├── .gitignore
├── pyproject.toml
└── README.md
```

**Nota:** el archivo de integración se encontraba anteriormente en `tests/tests/test_integracion_pdf.py`. Si todavía está allí, se recomienda moverlo a `tests/test_integracion_pdf.py`. Las carpetas de paquetes Python pueden incluir sus correspondientes archivos `__init__.py`.

### Responsabilidades por módulo

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Inicializa el sistema de logging, carga el tema QSS y lanza la aplicación Qt |
| `ui/main_window.py` | Contenedor principal, navegación y control del cierre normal |
| `ui/pages/home_page.py` | Presentación de herramientas y acceso a la conversión |
| `ui/pages/converter_page.py` | Selección del documento, elección de salida, barra de actividad y avisos |
| `ui/widgets/file_drop_widget.py` | Componente reutilizable para seleccionar o soltar PDF |
| `ui/styles/theme.qss` | Colores, tipografía y apariencia de la aplicación |
| `services/conversion_service.py` | Coordina validación y conversión |
| `document_engine/pdf_validator.py` | Revisa la legibilidad inicial y protección de documentos PDF |
| `document_engine/pdf_to_word.py` | Convierte y valida el DOCX; gestiona archivos temporales y publicación |
| `workers/conversion_worker.py` | Ejecuta el servicio en `QThread` y emite señales de resultado |
| `infrastructure/logger.py` | Configura registros locales con rotación |

## Flujo de conversión

```text
Usuario selecciona o arrastra un PDF
                  |
                  v
       Interfaz PySide6
       (converter_page.py)
                  |
                  v
      Trabajador QThread
     (conversion_worker.py)
                  |
                  v
      Servicio de conversión
      (conversion_service.py)
                  |
          +-------+--------+
          |                |
          v                v
    Validar PDF      Convertir PDF
 (pdf_validator.py)  (pdf_to_word.py)
          |                |
          |         Generar temporal
          |         Validar DOCX
          |         Publicar salida
          +-------+--------+
                  |
                  v
      Señal de éxito o error
                  |
                  v
       Interfaz informa resultado
```

El usuario selecciona un PDF y la ubicación de salida. El trabajador inicia la operación sin bloquear la interfaz; el servicio valida primero el PDF y luego solicita la conversión. El motor genera y valida un DOCX temporal antes de publicarlo, y las señales Qt permiten comunicar el resultado a la vista.

## Instalación y ejecución

### Requisitos

- Python 3.13, conforme a la configuración inicial de `pyproject.toml`.
- Git (para clonar el repositorio).
- Windows es el entorno donde se ha desarrollado y probado hasta la fecha.

### Configuración con Git Bash (Windows)

```bash
git clone https://github.com/TU_USUARIO/DocLab.git
cd DocLab

python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[dev]"
```

> Sustituye `TU_USUARIO` por la cuenta correspondiente antes de publicar el README. Si deseas instalar solo la aplicación, utiliza `python -m pip install -e .`.

### Iniciar DocLab

```bash
doclab
```

También puede ejecutarse con:

```bash
python -m doclab.main
```

### Uso básico

1. Abre DocLab.
2. Selecciona **Convertir** desde la navegación lateral o desde Inicio.
3. Selecciona o arrastra un archivo PDF.
4. Presiona **Convertir a Word** y elige una ubicación y nombre de salida.
5. Espera a que termine el procesamiento.
6. Revisa el documento `.docx` y verifica su formato y contenido.

**Consejo:** para las primeras conversiones, utiliza PDF con texto seleccionable y sin protección. Los PDF escaneados necesitarán un módulo OCR futuro.

## Pruebas automatizadas

Se utilizan pruebas unitarias y de integración con `pytest`.

Para ejecutarlas:

```bash
python -m pytest -v
```

### Cobertura funcional de la suite actual

**Motor de conversión (`test_pdf_to_word.py`):**

1. Rechaza un PDF inexistente.
2. Rechaza una extensión de origen incorrecta.
3. Rechaza una extensión de destino incorrecta.
4. Evita sobrescribir un archivo existente.
5. Detecta una carpeta de destino inexistente.
6. Publica un documento simulado sin dejar temporales.
7. Rechaza un DOCX simulado corrupto sin publicarlo.
8. Protege un destino creado simultáneamente por otro proceso.

**Integración PDF → DOCX (`test_integracion_pdf.py`):**

9. Genera un PDF de ejemplo, lo convierte con el motor real, abre el Word resultante y comprueba la presencia del texto esperado.

**Validador (`test_pdf_validator.py`):**

10. Acepta un PDF válido.
11. Rechaza un PDF inexistente.
12. Rechaza un archivo de texto con extensión `.pdf`.
13. Detecta un PDF cifrado que requiere contraseña.

**Último resultado comunicado:** 13 pruebas aprobadas. Este estado describe la última ejecución reportada durante el desarrollo; el resultado de futuras versiones deberá comprobarse ejecutando nuevamente la suite.

### Advertencia conocida

Durante las pruebas puede aparecer un `FutureWarning` asociado al nombre antiguo `fitz` que utiliza una dependencia indirecta. Para código propio se utiliza `import pymupdf`. La advertencia no equivale por sí sola a una prueba fallida.

## Limitaciones y aspectos pendientes

- La conversión puede modificar el diseño original de documentos con varias columnas, tablas complejas, formularios o imágenes.
- Los PDF escaneados no disponen todavía de un flujo OCR integrado.
- Los PDF protegidos con contraseña se detectan y rechazan; no existe todavía una opción de autenticación para el usuario.
- La validación de PDF identifica ciertos errores, pero no garantiza que todos los documentos dañados sean detectados de antemano.
- La verificación estructural del DOCX no implica que todos sus elementos visuales estén correctos.
- La publicación por enlaces físicos puede fallar en sistemas de archivos que no los soporten.
- La barra de actividad es indeterminada: todavía no indica porcentaje real.
- No existe cancelación segura de trabajos ni recuperación integral tras apagados abruptos.
- La integración del validador con los mensajes finales de la interfaz aún debe verificarse manualmente con PDF protegidos y corruptos.
- La distribución en un instalador para usuarios finales aún no está implementada.

## Hoja de ruta

### Próximas mejoras técnicas

- [ ] Verificar desde la interfaz los mensajes para PDF protegidos o corruptos.
- [ ] Añadir pruebas automatizadas del servicio de conversión y del trabajador.
- [ ] Mejorar limpieza y recuperación tras fallas y cierre inesperado.
- [ ] Gestionar cancelación de operaciones de larga duración.
- [ ] Incorporar progreso detallado y procesamiento masivo.
- [ ] Preparar empaquetado e instalador para Windows.

### Nuevas herramientas documentales

- [ ] Unir y dividir archivos PDF.
- [ ] Reordenar, rotar y extraer páginas.
- [ ] Comprimir PDF.
- [ ] Aplicar OCR a documentos escaneados.
- [ ] Extraer imágenes y tablas.
- [ ] Convertir entre otros formatos de documentos.
- [ ] Comparar documentos y detectar cambios.
- [ ] Evaluar la fidelidad visual de PDF → Word.
- [ ] Crear recetas de automatización documental.
- [ ] Explorar búsqueda documental y funciones de IA, preferiblemente con procesamiento local cuando sea viable.

## Principios de diseño

- **Separación de responsabilidades:** la interfaz presenta, el servicio coordina y el motor procesa.
- **Modularidad:** cada herramienta documental debe poder evolucionar de manera independiente.
- **Pruebas reproducibles:** emplear archivos temporales, documentos de ejemplo y simulaciones de error.
- **Privacidad:** privilegiar procesamiento local y evitar registrar información confidencial de los documentos.
- **Desarrollo incremental:** agregar nuevas capacidades sin comprometer las funciones estables.

## Licencias y contribuciones

La licencia de DocLab **aún no está definida**. Antes de distribuir públicamente versiones empaquetadas o comerciales se revisarán las licencias y condiciones aplicables a PySide6 y las dependencias documentales.

Las propuestas de mejoras, reportes de errores y contribuciones pueden canalizarse mediante los mecanismos de GitHub que se habiliten en el repositorio.

---

**DocLab** — Proyecto en desarrollo, enfocado en construir herramientas documentales útiles, extensibles y verificables mediante pruebas automatizadas.

---

# DocLab — Avances del proyecto: conversión PDF a Word con OCR

> **Actualización del desarrollo — octubre de 2026.** Esta sección continúa el README original y documenta las funcionalidades implementadas después de la versión inicial del conversor. En caso de contradicción con apartados históricos anteriores (por ejemplo, referencias a OCR «pendiente» o a solamente 13 pruebas), **este apartado describe el estado más reciente comprobado**. No se elimina el historial de avances anterior.

## Estado actual de la funcionalidad

**Estado: primera versión funcional completada y validada.**

DocLab permite elegir desde su interfaz gráfica entre dos modalidades de conversión de PDF a Word:

1. **Conversión tradicional:** utiliza `pdf2docx`, especialmente orientada a PDF con texto digital y estructuras compatibles.
2. **Conversión con OCR:** utiliza PyMuPDF y Tesseract integrado en el procesamiento OCR, con modelos de idioma locales para reconocer texto de páginas escaneadas e imágenes incrustadas, generar texto editable y conservar imágenes según la política actual de exportación.

**Validación comunicada durante el desarrollo:**

- **124 pruebas automatizadas aprobadas** mediante `pytest`.
- **3 pruebas manuales de la interfaz aprobadas:** PDF digital en modo tradicional, PDF escaneado en modo OCR y PDF mixto en modo OCR.
- No se comunicaron observaciones o fallos en estas tres pruebas manuales.

Las pruebas confirman los escenarios ejercitados; no garantizan una conversión idéntica al original para todos los PDF posibles.

## Funcionalidades nuevas

### 1. Inspección y clasificación del contenido PDF

- Validación previa del PDF, reutilizando el módulo existente `pdf_validator.py`.
- Identificación de páginas con y sin texto seleccionable.
- Clasificación de documentos como `con_texto`, `sin_texto` o `mixto`.
- Detección de páginas con imágenes y páginas que combinan texto digital con imágenes.
- Recuento de imágenes y registro de páginas donde aparecen.
- Análisis de cobertura de imágenes para señalar **posibles** páginas escaneadas; esta clasificación es heurística y no constituye una certeza sobre la naturaleza del documento.

**Módulos principales:** `pdf_content_detector.py`, `image_coverage.py` y `pdf_validator.py`.

### 2. Reconocimiento óptico de caracteres (OCR)

- Reconocimiento de palabras contenidas en imágenes de documentos PDF.
- Idiomas inicialmente configurados: **español (`spa`) e inglés (`eng`)**.
- Procesamiento de páginas escaneadas mediante OCR completo (`full=True`).
- Procesamiento de páginas con texto digital e imágenes mediante OCR parcial (`full=False`).
- Recuperación de texto por página y tratamiento explícito de errores de reconocimiento o de modelos de idioma ausentes.
- Extracción de texto y coordenadas de fragmentos (`bbox`) a partir de los resultados OCR.
- Distinción convencional entre texto digital y texto reconocido por OCR parcial mediante la fuente `GlyphLessFont` utilizada por PyMuPDF.
- **Motor OCR unificado:** permite extraer el texto y sus posiciones utilizando el mismo objeto `TextPage`, evitando ejecutar OCR dos veces sobre cada página que lo requiere dentro de ese flujo.

**Módulos principales:** `ocr_engine.py`, `ocr_document.py`, `ocr_text_blocks.py` y `ocr_unified.py`.

> La detección de páginas con imágenes no significa que todas sus imágenes contengan texto; pueden producirse reconocimientos innecesarios. El orden de lectura del OCR puede requerir ajustes en documentos complejos.

### 3. Análisis de estructura, imágenes y orden de lectura

- Obtención de bloques de texto e imagen mediante la información estructurada de PyMuPDF.
- Registro de coordenadas `(x0, y0, x1, y1)` y páginas de origen.
- Recuperación de datos binarios y formato de imágenes que aparecen en el PDF.
- Ordenamiento geométrico aproximado por número de página, posición vertical y posición horizontal.
- Construcción de planes de reconstrucción de Word basados en bloques y, posteriormente, en fragmentos OCR con coordenadas.

**Módulos principales:** `pdf_layout.py`, `pdf_image_extractor.py`, `pdf_reading_order.py`, `word_layout_plan.py` y `word_positioned_plan.py`.

> El orden geométrico no equivale necesariamente al orden semántico de lectura en PDF con varias columnas, cuadros de texto superpuestos o diagramación compleja.

### 4. Exportación de documentos Word editables

Se implementaron distintas estrategias de exportación, conservadas de forma modular para permitir comparación y mejoras posteriores:

| Módulo | Responsabilidad |
| --- | --- |
| `ocr_word_export.py` | Exporta a DOCX el texto obtenido por OCR, con separación entre páginas. |
| `ocr_word_visual.py` | Exporta texto e imágenes; omite la imagen de página completa cuando se aplica OCR completo. |
| `word_layout_export.py` | Genera el DOCX siguiendo un plan ordenado de bloques de texto e imágenes. |
| `word_layout_plan.py` | Construye un plan inicial con posiciones aproximadas del texto OCR. |
| `word_positioned_plan.py` | Construye un plan que utiliza las coordenadas recuperadas del texto OCR. |

Características de la exportación avanzada:

- Texto digital y texto OCR incorporados como contenido editable de Word.
- Imágenes insertadas en línea cuando corresponde.
- Saltos de página para conservar una separación aproximada respecto al PDF.
- Omisión de la imagen completa del escaneo cuando se exporta su texto reconocido.
- Asociación de imágenes a bloques mediante página y proximidad de coordenadas.
- Generación en archivo temporal, validación del DOCX y publicación sin sobrescribir un destino existente.

**Límite conocido:** mantener una imagen incrustada y exportar además sus palabras reconocidas puede producir duplicación *visual* del contenido. Tampoco se garantiza la ubicación exacta de las imágenes ni la reconstrucción íntegra de estilos, tablas y columnas.

### 5. Servicio de conversión OCR e integración con la interfaz

- **`services/ocr_conversion_service.py`:** define `ServicioConversionOCR`, responsable de coordinar el flujo completo desde un PDF hasta el DOCX.
- **`workers/ocr_conversion_worker.py`:** define `TrabajadorConversionOCR`, basado en `QThread`, y emite las señales `conversion_exitosa` y `conversion_fallida`.
- **`ui/pages/converter_page.py`:** incorpora un selector de modalidad con dos opciones: **Tradicional** y **Con OCR**.
- Se conserva el trabajador y servicio de conversión tradicional, sin sustituir el motor `pdf2docx`.
- Durante la operación se deshabilitan controles de selección y conversión, se muestra un indicador de actividad indeterminado y se comunican resultados o errores mediante la interfaz.
- Se contemplan mensajes específicos para PDF protegidos o corruptos, recursos OCR faltantes, errores de reconocimiento y archivos de destino existentes.
- La ventana principal mantiene su mecanismo de prevención de cierre normal mientras existe una conversión activa.

## Flujo técnico de conversión

```text
Usuario selecciona un PDF en la interfaz PySide6
                     |
                     v
            PaginaConversor
                     |
           Seleccion de modalidad
                /         \
               /           \
              v             v
       TRADICIONAL        CON OCR
              |             |
              v             v
   TrabajadorConversion   TrabajadorConversionOCR
              |             |
              v             v
   ServicioConversion     ServicioConversionOCR
              |             |
              v             v
          pdf2docx     procesar_ocr_unificado()
                            |
                            v
                     analizar_estructura_pdf()
                            |
                            v
                     extraer_imagenes_pdf()
                            |
                            v
                     crear_plan_word_posicionado()
                            |
                            v
                     exportar_plan_a_word()
               \           /
                \         /
                     v
             Documento .docx
                     |
                     v
           Senal de exito o error
                     |
                     v
             Interfaz informa resultado
```

## Organización de los módulos incorporados

Las siguientes rutas son relativas a `src/doclab/`:

```text
src/doclab/
├── document_engine/
│   ├── image_coverage.py
│   ├── pdf_content_detector.py
│   ├── ocr_engine.py
│   ├── ocr_document.py
│   ├── ocr_text_blocks.py
│   ├── ocr_unified.py
│   ├── ocr_word_export.py
│   ├── ocr_word_visual.py
│   ├── pdf_layout.py
│   ├── pdf_image_extractor.py
│   ├── pdf_reading_order.py
│   ├── word_layout_plan.py
│   ├── word_positioned_plan.py
│   └── word_layout_export.py
├── resources/
│   └── tessdata/
│       ├── .gitkeep
│       ├── spa.traineddata    # Local, ignorado por Git
│       └── eng.traineddata    # Local, ignorado por Git
├── services/
│   └── ocr_conversion_service.py
├── workers/
│   └── ocr_conversion_worker.py
└── ui/
    └── pages/
        └── converter_page.py  # Selector Tradicional / Con OCR
```

Los archivos anteriores complementan los componentes ya descritos en el README original. `image_coverage.py` y `pdf_content_detector.py` se habían incorporado durante etapas intermedias del proyecto; aquí se registran junto al resto del flujo OCR.

## Dependencias utilizadas en esta ampliación

| Tecnología | Uso |
| --- | --- |
| PyMuPDF (`pymupdf`) | Apertura, inspección, OCR, extracción de imágenes y coordenadas. |
| Tesseract integrado mediante PyMuPDF | Reconocimiento óptico local del texto de imágenes. |
| `spa.traineddata` y `eng.traineddata` | Modelos locales para español e inglés. |
| `python-docx` | Construcción, lectura y comprobación de documentos Word. |
| `pdf2docx` | Motor independiente de la conversión tradicional. |
| PySide6 / `QThread` / `Signal` | Interfaz gráfica, procesamiento fuera del hilo principal y comunicación de resultados. |
| `pytest` | Pruebas unitarias y de integración. |

La configuración de dependencias principales se actualizó en `pyproject.toml` para incluir `pymupdf` y `python-docx`. El desarrollo y pruebas se realizaron en Python 3.13 sobre Windows.

## Instalación desde el repositorio: recursos OCR

> **Importante:** el repositorio excluye deliberadamente los modelos de idioma `.traineddata`. El código puede clonarse desde GitHub, pero para utilizar el OCR en otro equipo de desarrollo hay que añadir manualmente los recursos.

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/yurilealjaque/DocLab-Demo.git
   cd DocLab-Demo
   ```

2. Crear y activar el entorno virtual en Git Bash (Windows):

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate
   ```

3. Instalar DocLab con dependencias de desarrollo:

   ```bash
   python -m pip install -e ".[dev]"
   ```

4. Descargar los modelos oficiales `spa.traineddata` y `eng.traineddata` desde el proyecto [`tesseract-ocr/tessdata_fast`](https://github.com/tesseract-ocr/tessdata_fast) y colocarlos en:

   ```text
   src/doclab/resources/tessdata/
   ```

5. Ejecutar la aplicación:

   ```bash
   doclab
   ```

   La alternativa `python -m doclab.main` depende del punto de entrada implementado en la aplicación.

El motor se desarrolló para utilizar recursos OCR locales a través de PyMuPDF y no depender de que el usuario de la aplicación instale manualmente `tesseract.exe` en el PATH. **Todavía no existe un instalador autónomo de Windows**: esa distribución se abordará al final del proyecto, junto con el empaquetado de dependencias y modelos.

## Cómo utilizar las dos modalidades

1. Abrir DocLab y acceder a **Convertir**.
2. Seleccionar o arrastrar un documento PDF.
3. Escoger una modalidad:
   - **Tradicional:** recomendada para PDF digitales cuando se busca preservar mejor su maquetación.
   - **Con OCR:** recomendada para documentos escaneados o PDF mixtos con palabras dentro de imágenes.
4. Presionar **Convertir a Word**.
5. Elegir un nombre y una ruta `.docx` que no estén ocupados.
6. Esperar el resultado y revisar el documento final en Word.

La modalidad OCR produce texto editable, pero no debe interpretarse como una reproducción visual exacta del PDF de origen.

## Calidad y pruebas

**Último estado confirmado: 124 pruebas automatizadas aprobadas.**

La suite incluye escenarios sobre:

- Validación de archivos PDF, protección por contraseña y errores de lectura.
- Detección de texto, imágenes, cobertura y posibles escaneos.
- Reconocimiento OCR real con archivos PDF generados por los tests.
- Diferenciación entre páginas digitales, escaneadas, mixtas y vacías.
- Recuperación de fragmentos de texto y sus coordenadas.
- Comprobación de una ejecución OCR por página en el motor unificado.
- Extracción de imágenes, estructura visual, orden de bloques y planes de reconstrucción.
- Generación de DOCX, conservación de imágenes y protección frente a sobrescritura.
- Pruebas de integración de PDF → OCR → Word y de los trabajadores de conversión.

Para ejecutar la suite:

```bash
python -m pytest -v --tb=short
```

### Verificaciones manuales completadas

| Caso | Modalidad | Resultado comunicado |
| --- | --- | --- |
| PDF con texto digital | Tradicional | Correcto |
| PDF escaneado con palabras dentro de una imagen | Con OCR | Correcto |
| PDF mixto con texto digital e imagen con palabras | Con OCR | Correcto |

No se reportaron observaciones en esas tres comprobaciones. La cobertura de escenarios visuales complejos y documentos reales variados todavía es limitada.

## Política de Git y archivos locales

El archivo `.gitignore` excluye, entre otros elementos:

- Entornos virtuales, cachés, logs y resultados temporales.
- Archivos `.traineddata` ubicados en `src/doclab/resources/tessdata/`.
- Carpetas locales de pruebas manuales y archivos de salida que coincidan con las reglas configuradas.

La carpeta `tessdata` se representa mediante `.gitkeep` para conservar su ubicación sin publicar los modelos binarios. Los modelos permanecen en el equipo del desarrollador y deben obtenerse nuevamente al clonar el proyecto en otro entorno.

> No deben incorporarse al repositorio documentos reales con datos confidenciales ni claves o configuraciones privadas.

## Limitaciones conocidas de la primera versión OCR

1. **Fidelidad visual:** tablas complejas, varias columnas, estilos tipográficos, encabezados, pies de página y elementos superpuestos pueden perder su distribución original.
2. **Orden de lectura:** las coordenadas permiten una ordenación geométrica aproximada, pero no garantizan lectura semántica correcta en diseños complejos.
3. **Imágenes con texto:** en PDF mixtos, el contenido de una imagen puede conservarse gráficamente y aparecer además como texto OCR editable, causando duplicación visual.
4. **Formato de imágenes:** algunas estrategias de exportación admiten inicialmente PNG y JPEG y pueden rechazar otros formatos.
5. **Rendimiento:** el OCR unificado elimina repeticiones del reconocimiento dentro de su flujo, pero el sistema aún puede abrir o inspeccionar el mismo documento varias veces.
6. **Progreso:** la interfaz utiliza una barra indeterminada, sin porcentaje real por página.
7. **Cancelación y cierres forzosos:** no hay un mecanismo completo de cancelación segura ni garantía de recuperación tras terminación abrupta.
8. **Archivos de salida:** la publicación mediante `os.link()` depende de la compatibilidad del sistema de archivos; no garantiza portabilidad universal.
9. **Reconocimiento:** los resultados dependen de la calidad del escaneo, resolución, idiomas y complejidad del contenido.
10. **Identidad de resultados:** algunos componentes comprueban cantidades y números de páginas, pero todavía no verifican de forma criptográfica que todos los resultados intermedios provengan del mismo PDF.
11. **Distribución:** no existe todavía ejecutable independiente ni instalador de Windows para usuarios finales.

## Hoja de ruta actualizada

### Funcionalidad PDF → Word

- [x] Conversión tradicional con `pdf2docx`.
- [x] Validación básica y protección frente a sobrescritura.
- [x] Procesamiento en segundo plano e integración gráfica.
- [x] Inspección y clasificación de contenido PDF.
- [x] Reconocimiento OCR de documentos escaneados y mixtos.
- [x] Procesamiento OCR de varias páginas.
- [x] Recuperación de texto y coordenadas en un flujo unificado.
- [x] Extracción de imágenes y análisis de estructura.
- [x] Exportación de Word con texto editable e imágenes.
- [x] Plan básico de reconstrucción y ordenamiento de bloques.
- [x] Selector de modalidad tradicional / OCR en la interfaz.
- [x] Suite de 124 pruebas automatizadas aprobadas.
- [x] Tres escenarios manuales principales aprobados.

### Mejoras futuras

- [ ] Reconstrucción mejorada de tablas, columnas, estilos y maquetación.
- [ ] Reducción de aperturas y recorridos repetidos de PDF.
- [ ] Progreso detallado por página y cancelación segura.
- [ ] Pruebas adicionales con documentos reales variados, archivos grandes y casos límite.
- [ ] Comparación automática de fidelidad entre PDF original y DOCX.
- [ ] Conversión por lotes e historial local de operaciones.
- [ ] Nuevas herramientas: unir, dividir, rotar, reordenar y comprimir PDF.
- [ ] Empaquetado como ejecutable autónomo, inclusión de modelos OCR e instalador de Windows **al final del proyecto**.

## Alcance de este hito

La primera versión funcional de **conversión PDF → Word con OCR** está implementada y validada en los escenarios descritos. Este hito cierra la integración básica del OCR, pero **no implica que el proyecto DocLab en su conjunto esté terminado**: su arquitectura permite continuar desarrollando nuevas herramientas y mejorar la fidelidad de conversión.

---

**DocLab — Convierte, organiza y transforma tus documentos.**

# DocLab — Continuación del README: unión y división de PDF

> **Actualización de octubre de 2026.** Este documento **continúa**, no sustituye, el `README.md` existente. Documenta los avances posteriores al capítulo sobre conversión PDF a Word con OCR. Los apartados antiguos del README se conservan como historial, aunque mencionen como «pendientes» herramientas que ya están implementadas.

**Repositorio:** https://github.com/yurilealjaque/DocLab-Demo  
**Entorno principal:** Windows, Python 3.13, PySide6, PyMuPDF, Git Bash, `.venv`.  
**Estado:** prototipo funcional con conversión PDF a Word tradicional y OCR, unión de PDF y tres modalidades de división.  
**Versión:** se propuso `v0.3.0` («PDF Split & Merge»). Su creación/publicación debe verificarse con `git tag --list` antes de afirmarla como definitiva.

---

## 1. Resumen de los avances

Se incorporaron dos herramientas nuevas:

- **Unir PDF:** seleccionar varios documentos, ordenar su secuencia y generar un archivo resultante.
- **Dividir PDF:** extraer un rango continuo, elegir páginas específicas o separar todas las páginas en archivos independientes.

Ambas siguen la arquitectura modular de DocLab:

```text
Interfaz PySide6
       ↓
Trabajador QThread (señales éxito/error)
       ↓
Servicio de aplicación
       ↓
Motor documental PyMuPDF
       ↓
Documento(s) PDF de salida
```

El menú lateral y la pantalla Inicio ofrecen acceso a **Convertir**, **Unir PDF** y **Dividir PDF**. Los estilos visuales siguen centralizados en QSS.

## 2. Herramienta «Unir PDF»

### 2.1. Motor documental

**Ruta:** `src/doclab/document_engine/pdf_merger.py`

- Exige como mínimo dos documentos PDF.
- Valida entradas mediante el módulo reutilizable `pdf_validator.py`.
- Detecta archivos inexistentes, corruptos o protegidos en los escenarios contemplados.
- Respeta el orden de la lista seleccionada.
- Genera y valida el PDF resultante, incluida su cantidad de páginas.
- Utiliza archivos temporales y publicación sin sobrescritura mediante `os.link()`.
- Limpia temporales al finalizar y ante excepciones controladas.

**Precisión:** inicialmente se utilizó `insert_pdf()`; ante una incidencia de pérdida visual se ensayó una implementación con `show_pdf_page()`. **Este cambio no resolvió el problema**. Confirmar el algoritmo vigente consultando el código local antes de modificarlo nuevamente.

### 2.2. Servicio y trabajador

- `src/doclab/services/pdf_merge_service.py`: clase `ServicioUnionPDF`; método `unir(rutas_origen, ruta_destino)`.
- `src/doclab/workers/pdf_merge_worker.py`: clase `TrabajadorUnionPDF(QThread)`, con señales `union_exitosa(str)` y `union_fallida(str)`.
- El servicio delega; el trabajador procesa en un hilo secundario y notifica a la interfaz.

### 2.3. Pantalla gráfica

**Ruta:** `src/doclab/ui/pages/pdf_merge_page.py`

- Selección de varios archivos con `QFileDialog`.
- Lista de documentos y contador.
- Evita duplicados por ruta normalizada.
- Reordenamiento con «Subir» y «Bajar» y eliminación de la selección sin borrar originales.
- Sincronización entre el orden visual y la lista `rutas_pdf`.
- Selección de destino, prevención de sobrescritura, barra de actividad, mensajes de éxito/error.
- Desactivación temporal de controles durante la operación.
- Acceso desde el menú lateral y desde Inicio.

### 2.4. Incidencia conocida: DOC-001 — Pérdida de contenido visual

**Caso comunicado:** unión de tres documentos reales:

| Documento | Páginas |
| --- | ---: |
| `Guia_Exhaustiva_QA_Clase_8_Bruno.pdf` | 56 |
| `Manual_profesional_QA_Bruno_Clase_9_AMPLIADO.pdf` | 39 |
| `Dieta y colelitiasis.pdf` | 2 |
| **Total** | **97** |

El resultado contiene **97 páginas**, pero la **página 96** (primera del tercer documento) aparece en gran parte vacía o pierde contenido visual. PyMuPDF puede extraer texto de la página original; esto no demuestra que el original esté defectuoso. Se requiere diagnóstico.

**Intento no concluyente:** cambiar la copia de páginas a `show_pdf_page()` no resolvió la incidencia.

**Investigación pendiente:**

1. Comparar la página original y la página 96 mediante imágenes renderizadas con `get_pixmap()` a igual resolución.
2. Comparar texto con `get_text()` y examinar sus coordenadas.
3. Inspeccionar recursos, fuentes, imágenes, anotaciones, transparencia y capas opcionales de los documentos.
4. Preparar un PDF de ejemplo reproducible y redistribuible para crear una prueba de regresión.
5. Evaluar alternativas solo después de identificar el origen del problema.
6. No interpretar el recuento correcto de páginas como garantía de fidelidad visual.

**Prioridad:** importante antes de distribuir la aplicación a terceros.

## 3. Herramienta «Dividir PDF»

### 3.1. Motor documental

**Ruta:** `src/doclab/document_engine/pdf_splitter.py`

Se incorporaron tres funciones públicas:

#### A. `extraer_rango_pdf(ruta_origen, ruta_destino, pagina_inicio, pagina_fin)`

Extrae un intervalo continuo e **incluye ambos extremos**. Las páginas que indica el usuario empiezan en 1, mientras que PyMuPDF trabaja internamente con índices desde 0.

```python
extraer_rango_pdf("clase.pdf", "resumen.pdf", 3, 7)
# Genera cinco páginas: 3, 4, 5, 6 y 7.
```

Valida tipos enteros, límites, orden del rango, existencia del archivo de origen, destino adecuado, carpeta existente y no sobrescritura. Trabaja con un archivo temporal, verifica el número de páginas y publica mediante `os.link()`.

#### B. `extraer_paginas_pdf(ruta_origen, ruta_destino, paginas)`

Extrae páginas individuales en el orden elegido:

```python
extraer_paginas_pdf("clase.pdf", "seleccion.pdf", [1, 4, 8])
```

- Admite una lista o tupla no vacía.
- Rechaza elementos no enteros, repetidos o fuera del documento.
- Conserva el orden recibido, incluso si es `[8, 1, 4]`.
- Verifica la cantidad de páginas resultante.
- Evita sobrescritura y limpia el temporal.

**Decisión actual:** no permitir duplicados en la selección para evitar repeticiones accidentales.

#### C. `separar_paginas_pdf(ruta_origen, carpeta_destino)`

Produce un PDF por cada página. Ejemplo para un archivo de cuatro páginas:

```text
informe_pagina_001.pdf
informe_pagina_002.pdf
informe_pagina_003.pdf
informe_pagina_004.pdf
```

- La carpeta destino debe existir.
- Verifica previamente los nombres de salida para evitar colisiones.
- Genera y valida cada PDF en una carpeta `TemporaryDirectory()`.
- Publica mediante `os.link()`; si falla durante la publicación, intenta retirar únicamente los archivos que la operación creó.
- No garantiza atomicidad ante apagones, interrupción forzosa u operaciones externas concurrentes.

### 3.2. Servicio de división

**Ruta:** `src/doclab/services/pdf_split_service.py`

La clase `ServicioDivisionPDF` expone:

- `extraer_rango(...)`
- `extraer_paginas(...)`
- `separar_todas(...)`

Cada método delega en su función correspondiente del motor documental y propaga los errores, sin duplicar las validaciones.

### 3.3. Trabajador QThread

**Ruta:** `src/doclab/workers/pdf_split_worker.py`

La clase `TrabajadorDivisionPDF(QThread)` recibe un modo:

| Modo | Operación |
| --- | --- |
| `rango` | Extraer intervalo continuo |
| `paginas` | Extraer selección de páginas |
| `todas` | Generar un PDF por página |

Emite `division_exitosa(object)` o `division_fallida(str)`. Normaliza los resultados a una lista de rutas (`list[str]`) tanto si el motor devuelve un único archivo como si genera muchos. Se probó que `start()` ejecuta el servicio fuera del hilo principal.

### 3.4. Interfaz PySide6

**Ruta:** `src/doclab/ui/pages/pdf_split_page.py`

Clase `PaginaDivisionPDF(QWidget)`:

- Selección de origen y validación con `validar_pdf()`.
- Presentación del total de páginas.
- Selector de modalidad (`QComboBox`).
- Rango con `QSpinBox`.
- Páginas específicas con `QLineEdit` y valores separados por coma.
- Selección de archivo de salida o carpeta según corresponda.
- Método `preparar_solicitud()` para validar antes de ejecutar.
- `QProgressBar` indeterminado, mensajes de resultado y bloqueo de controles durante procesamiento.
- Protección ante cierre individual de la página durante una operación activa.

### 3.5. Integración con la ventana principal

Se actualizaron:

- `src/doclab/ui/main_window.py`: registro de `PaginaDivisionPDF`, botón lateral, navegación y controles de cierre durante conversión, unión y división.
- `src/doclab/ui/pages/home_page.py`: señal `abrir_division_pdf = Signal()` y tarjeta habilitada.

**Error de integración encontrado y corregido:** `AttributeError: 'PaginaInicio' object has no attribute 'abrir_division_pdf'`. La causa fue conectar la señal en `main_window.py` antes de declararla en `home_page.py`.

El usuario confirmó que DocLab volvió a abrir, que la navegación se veía funcional y que las **tres modalidades de división** pasaron la revisión manual posterior.

## 4. Calidad y pruebas automatizadas

Se trabajó de forma incremental: implementar motor → probar → servicio → probar → trabajador → probar → interfaz → probar → integración manual.

| Grupo | Pruebas comunicadas como aprobadas |
| --- | ---: |
| Motor de unión | 10 |
| Servicio de unión | 2 |
| Trabajador de unión | 3 |
| Interfaz de unión | 6 |
| **Subtotal unión** | **21** |
| Motor de división | 15 |
| Servicio de división | 4 |
| Trabajador de división | 5 |
| Interfaz de división | 9 |
| **Subtotal división** | **33** |
| **Total de pruebas descritas en estos grupos** | **54** |

**Advertencia:** este subtotal por grupos **no equivale** al recuento confirmado de la suite completa en su estado actual. El usuario comunicó que toda la suite pasó, pero se debe consultar el resultado exacto al ejecutar nuevamente `pytest`.

Estrategias utilizadas: PDF sintéticos identificables, rangos y valores límite, documentos corruptos/protegidos, hashes SHA-256 para integridad del original, `monkeypatch` para simular fallos de publicación, comprobación de limpieza de temporales, pruebas de señales y de ejecución real en hilo secundario, y estados de interfaz.

```bash
python -m pytest tests/test_pdf_splitter.py -v --tb=short
python -m pytest tests/test_pdf_split_service.py -v --tb=short
python -m pytest tests/test_pdf_split_worker.py -v --tb=short
python -m pytest tests/test_pdf_split_page.py -v --tb=short
python -m pytest -q --tb=short
```

**Pendientes de calidad:** pruebas de ciclo completo de eventos Qt, cancelación, cierres forzosos, rutas concurrentes, rendimiento con PDF grandes y regresión de fidelidad visual.

## 5. Estructura ampliada del proyecto

Los módulos de esta etapa complementan los de conversión y OCR del README anterior:

```text
src/doclab/
├── document_engine/
│   ├── pdf_merger.py
│   └── pdf_splitter.py
├── services/
│   ├── pdf_merge_service.py
│   └── pdf_split_service.py
├── workers/
│   ├── pdf_merge_worker.py
│   └── pdf_split_worker.py
└── ui/
    ├── main_window.py
    └── pages/
        ├── home_page.py
        ├── pdf_merge_page.py
        └── pdf_split_page.py

tests/
├── test_pdf_merger.py
├── test_pdf_splitter.py
├── test_pdf_split_service.py
├── test_pdf_split_worker.py
└── test_pdf_split_page.py
```

Las pruebas de unión de servicio, trabajador e interfaz también existen; sus nombres exactos se deben confirmar en el árbol actual del repositorio si se reorganizaron.

## 6. Git, tags y archivos locales

Mensaje descriptivo propuesto para el commit de división:

```text
feat(pdf): implementar modulo completo de division y extraccion de paginas
```

Se propuso crear el tag `v0.3.0`, pero la existencia y publicación deben comprobarse:

```bash
git status
git log -3 --oneline
git tag --list --sort=-version:refname
git show v0.3.0 --no-patch
```

El `.gitignore` excluye `pruebas_manuales/` y recursos OCR locales `src/doclab/resources/tessdata/*.traineddata`; no deben publicarse documentos privados ni modelos binarios innecesarios. Evitar ignorar todos los archivos `.pdf`, `.docx` o imágenes de manera global porque se podrían necesitar fixtures públicos para pruebas.

## 7. Deuda técnica y limitaciones conocidas

1. **DOC-001:** una página de un PDF unido pierde contenido visual; el uso de `show_pdf_page()` no resolvió la incidencia.
2. La comprobación de cantidad de páginas no garantiza fidelidad del contenido.
3. Advertencia sobre `fitz`: identificar importación directa o indirecta que aún utilice la API deprecada; preferir `import pymupdf` cuando corresponda.
4. La barra de actividad es indeterminada, sin progreso porcentual real.
5. No hay cancelación segura general para operaciones largas.
6. `os.link()` depende de condiciones del sistema de archivos.
7. Mejorar gestión de cierre y vida útil de `QThread` bajo errores y operaciones repetidas.
8. Pruebas visuales, de accesibilidad y de rendimiento aún limitadas.
9. No existe todavía instalador de Windows para usuario final.

## 8. Hoja de ruta actualizada

### Etapa 4 — Robustez y calidad (**próxima etapa acordada**)

- [ ] Diagnosticar DOC-001 comparando texto, recursos y renderizado de páginas original/salida.
- [ ] Crear prueba de regresión con un documento reproducible y apto para el repositorio.
- [ ] Corregir solo después de disponer de evidencia del origen.
- [ ] Verificar cierre seguro, señales y ciclo de vida de trabajadores.
- [ ] Revisar errores de publicación y limpieza de archivos temporales.
- [ ] Localizar el origen de la advertencia `fitz`.
- [ ] Ejecutar suite completa y comprobar resultados manualmente.

### Etapa 5 — Experiencia de usuario

- [ ] Progreso real cuando el motor permita medirlo.
- [ ] Mejorar mensajes y facilitar apertura de resultados.
- [ ] Evaluar vista previa de páginas y optimización de interfaz.

### Etapa 6 — Funcionalidades nuevas (**por debatir**) 

La lista anterior de herramientas genéricas **no está cerrada**. El usuario propone una función especialmente útil: **convertir fotos tomadas en clases a PDF**.

#### Propuesta de producto: Fotografías de clases → PDF

**Necesidad:** el estudiante fotografía diapositivas de PowerPoint proyectadas en una pizarra o pantalla porque no dispone del archivo original. Quiere reunir esas fotografías en un documento ordenado y legible para estudiar.

**MVP sugerido:**

1. Importar múltiples fotos JPG, JPEG y PNG desde cámara o celular.
2. Mostrar miniaturas y permitir reordenar, quitar y girar fotos.
3. Respetar orientación EXIF.
4. Crear un PDF con una imagen por página y orientación/tamaño configurables.
5. Guardar localmente sin sobrescribir documentos.
6. Validar el PDF generado y probar distintos tamaños/resoluciones.

**Mejoras posteriores que requieren más investigación:**

- Detección de bordes de una diapositiva proyectada.
- Corrección de perspectiva para fotos tomadas desde un costado del aula.
- Recorte de pared, pizarra, mesas u otros elementos ajenos a la proyección.
- Ajuste moderado de contraste, iluminación y nitidez.
- OCR opcional para hacer el PDF buscable.
- Gestión de fotografías borrosas, reflejos, sombras y texto ilegible.
- Compatibilidad HEIC/HEIF según bibliotecas disponibles.

**Límite de alcance:** producir un PDF de fotografías legibles **no equivale** a reconstruir un PowerPoint original y editable. Tampoco es posible recuperar fielmente información que la cámara no capturó por desenfoque, saturación o recorte.

**Arquitectura posible:** `PaginaFotosPDF` → `TrabajadorFotosPDF` → `ServicioFotosPDF` → motor de imágenes/PDF, reutilizando la organización existente. Se debe debatir su ubicación y prioridad con el usuario antes de codificar.

### Etapa 7 — Distribución en Windows

- [ ] Preparar empaquetado e inclusión de recursos OCR.
- [ ] Validar en Windows sin Python de desarrollo.
- [ ] Preparar instalador, revisar licencias y dependencias.

## 9. Contexto para continuar en una conversación nueva

**Proyecto:** DocLab, aplicación local Python 3.13/PySide6 en Windows, con arquitectura UI → QThread → Servicio → Motor.

**GitHub:** https://github.com/yurilealjaque/DocLab-Demo.

**Funcionalidades funcionales:** PDF→Word tradicional y OCR; Unir PDF con incidencia visual abierta; Dividir PDF con tres modalidades probadas.

**Estilo de colaboración:** explicaciones didácticas en español chileno, variables en español, cambios incrementales, scripts completos cuando se soliciten, indicar rutas exactas, `pytest` tras cada incremento, protección de código estable y no atribuir errores a una causa sin demostrarla.

**Al retomar:** revisar README histórico y esta continuación, consultar el código más reciente del repo o los archivos locales antes de sugerir reemplazos y comenzar Etapa 4 por diagnóstico de fidelidad. La nueva idea de **fotografías de clases a PDF** queda anotada para debatir y diseñar en la Etapa 6.

**Comandos útiles:**

```bash
source .venv/Scripts/activate
doclab
python -m pytest -q --tb=short
git status
git log -1 --oneline
git tag --list --sort=-version:refname
```

---

**DocLab — Convierte, organiza y transforma tus documentos.**

# DocLab — Continuación del README: Etapa 5 (UI/UX)

> **Actualización: octubre de 2026.** Este apartado se añade **al final** de `README.md`; no reemplaza el historial anterior. Documenta el rediseño y la mejora de experiencia de usuario posteriores a la incorporación de convertir, unir y dividir PDF. Algunos apartados históricos del README describen estados anteriores y deben interpretarse según la fecha de cada hito.

## 1. Objetivo de la etapa

Consolidar una interfaz de escritorio **profesional, coherente, intuitiva y accesible para usuarios no técnicos**, sin alterar innecesariamente los motores documentales que ya funcionan. Se adoptó una identidad visual **grafito y violeta** y una metodología de cambios pequeños con revisión manual y pruebas automatizadas.

Principios aplicados:

- **Una tarea por pantalla:** Inicio permite elegir qué hacer; Convertir, Unir y Dividir concentran las operaciones documentales.
- **Instrucciones claras:** explicar qué hace cada opción, cuándo usarla y qué resultado esperar.
- **Jerarquía de acciones:** distinguir botones principales de acciones secundarias y representar estados deshabilitados.
- **Retroalimentación:** comunicar progreso, éxito, fallas y condiciones previas sin ambigüedad.
- **Diseño adaptable:** evitar que etiquetas, campos y botones se corten al reducir el tamaño de la ventana.
- **Estabilidad:** conservar señales, validaciones y procesamiento mediante `QThread`; validar cada cambio.

## 2. Identidad visual y estilos

**Archivo principal:** `src/doclab/ui/styles/theme.qss`.

- Paleta oscura basada en grafito, con violeta para navegación activa, foco y acciones principales.
- Botones secundarios diferenciados de la acción principal.
- Mejora de contraste y legibilidad de títulos, textos secundarios, listas y controles de entrada.
- Fondos transparentes para etiquetas `QLabel` donde corresponde, para evitar rectángulos negros sobre tarjetas o zonas de selección.
- Estilos de listas, selecciones, campos, estados deshabilitados y barras de progreso.
- Estilos de `QGroupBox` para destacar secciones de formularios con bordes y encabezados reconocibles.

Se procura mantener las reglas compartidas en QSS; algunos componentes especiales aún tienen estilos locales en Python y pueden unificarse en una mejora posterior.

## 3. Pantalla Inicio: acceso a herramientas

**Archivo:** `src/doclab/ui/pages/home_page.py`.

- Se eliminó de **Inicio** el área «Arrastra tu archivo PDF aquí», porque podía hacer pensar que todas las operaciones comenzaban con una misma selección de archivo.
- Inicio funciona ahora como **catálogo de herramientas**, con tarjetas que explican su propósito y permiten navegar a **Convertir PDF a Word**, **Unir PDF** y **Dividir PDF**.
- Las herramientas futuras se muestran como **no disponibles**, con una descripción de su finalidad prevista.
- Se incorporó desplazamiento vertical con `QScrollArea` para que las tarjetas permanezcan accesibles en ventanas pequeñas.
- Se retiró la conexión antigua que enviaba un PDF directamente desde Inicio hacia Convertir; la selección de documentos se mantiene dentro de cada herramienta.

**Integración:** `src/doclab/ui/main_window.py` mantiene la navegación entre pantallas y las verificaciones de cierre durante operaciones activas.

## 4. Convertir PDF a Word: selector y explicaciones

**Archivos:** `src/doclab/ui/pages/converter_page.py` y `src/doclab/ui/widgets/file_drop_widget.py`.

- La zona de arrastrar y soltar **se conserva en Convertir**, donde su propósito es inequívoco.
- Se redujo su altura y se ajustaron márgenes y textos para aprovechar mejor el espacio.
- El selector diferencia los dos casos de uso: **PDF digital — conversión tradicional** y **PDF escaneado o con imágenes — OCR**.
- Se añadieron explicaciones dinámicas y advertencias razonables: PDF con texto seleccionable para conversión tradicional; PDF escaneado o con texto en imágenes para OCR.
- La explicación se presenta dentro de una tarjeta informativa grafito con acento violeta.
- Los identificadores internos de las modalidades (`tradicional` y `ocr`) se conservaron, así como los trabajadores y la lógica de conversión.

**Error corregido durante el desarrollo:** se intentó pasar el valor de retorno de `setStyleSheet()` a `addWidget()`. Como `setStyleSheet()` devuelve `None`, Qt producía un `RuntimeError`. La corrección separó la aplicación del estilo de la incorporación del widget al diseño. Es un ejemplo de error de ejecución que una comprobación de sintaxis (`py_compile`) no detecta.

## 5. Unir PDF: orden y estado de documentos

**Archivo:** `src/doclab/ui/pages/pdf_merge_page.py`.

- Se incorporó un resumen de **cantidad de archivos, páginas detectadas y tamaño acumulado** de los PDF seleccionados.
- La lectura de páginas se realiza con PyMuPDF; si algún archivo no puede leerse, la interfaz lo informa en el resumen sin presentar un total como plenamente verificado.
- Se mejoraron los mensajes de éxito, error y advertencia por selección insuficiente.
- La pantalla presenta instrucciones para agregar, ordenar y combinar archivos.
- Un estado vacío explica qué aparecerá en la lista y qué acciones podrá realizar el usuario.
- Los controles de movimiento y eliminación se habilitan o deshabilitan según la selección y la posición del archivo.
- La unión requiere al menos dos documentos; durante el procesamiento se bloquean los controles pertinentes.
- Se ajustó la distribución y se incorporó desplazamiento para reducir recortes o superposiciones en ventanas de menor tamaño.

**La incidencia DOC-001 sigue abierta:** se observó pérdida de contenido visual en una página de un PDF unido. Un recuento correcto de páginas no implica fidelidad visual. El rediseño de la GUI no resuelve ni descarta esta incidencia; debe diagnosticarse antes de distribuir DocLab a terceros.

## 6. Dividir PDF: modalidades y adaptación

**Archivo:** `src/doclab/ui/pages/pdf_split_page.py`.

La pantalla mantiene las tres modalidades existentes:

| Modalidad | Resultado esperado |
| --- | --- |
| `rango` | Un PDF que incluye todas las páginas entre los dos extremos indicados. |
| `paginas` | Un PDF con las páginas específicas indicadas, separadas por comas. |
| `todas` | Un PDF individual por cada página del original. |

Mejoras de UI/UX:

- Tarjeta informativa que cambia de explicación al seleccionar otra modalidad, incluyendo ejemplos concretos.
- Grupos visuales para **documento de origen**, **modalidad de división** y **destino**.
- Incorporación de `QScrollArea` y restricciones de tamaño para evitar que se corten las explicaciones y los campos cuando falta altura.
- Botón principal de división diferenciado visualmente.
- Mejora del indicador de actividad: el objetivo es mostrar la barra solamente durante una operación y conservar el mensaje de resultado tras finalizar.

La selección de origen, la validación de páginas, la elección del destino, las comprobaciones de datos y el procesamiento mediante `TrabajadorDivisionPDF` continúan separados de los estilos de la pantalla.

## 7. Validación y metodología

Durante la etapa se siguió el ciclo **cambio localizado → revisión de sintaxis → pruebas automatizadas → comprobación manual de interfaz**. Las capturas de la aplicación permitieron detectar problemas que no necesariamente aparecen en pruebas unitarias, como solapamiento de texto y campos recortados.

Comandos habituales desde la raíz del proyecto, con `.venv` activado:

```bash
# Verificar sintaxis de un archivo Python modificado.
python -m py_compile src/doclab/ui/pages/pdf_split_page.py

# Ejecutar la suite completa.
python -m pytest -q --tb=short

# Revisar visualmente las pantallas y operaciones.
doclab
```

En una ejecución de esta etapa se comunicaron **185 pruebas aprobadas y 2 errores de construcción de la interfaz**; tras corregir la tarjeta del conversor, el usuario informó que las pruebas volvieron a pasar. **No se fija aquí un recuento definitivo**: puede variar al incorporar nuevas pruebas y debe consultarse en la salida de `pytest` correspondiente a cada commit.

Se recomienda conservar pruebas para los estados de botones y las transiciones de la interfaz, además de la verificación manual con PDF reales.

## 8. Cierre de la Etapa 5 y límites

La Etapa 5 se considera **suficientemente madura para avanzar**, sujeto a que la suite de pruebas y las tres operaciones principales continúen funcionando en la revisión final. No se declara perfección visual ni compatibilidad universal.

Mejoras de interfaz que **no bloquean** la siguiente etapa:

- Sustituir símbolos provisionales por iconografía SVG consistente.
- Revisar navegación por teclado, accesibilidad y contraste.
- Probar distintas resoluciones y escalados de Windows.
- Unificar gradualmente estilos locales con `theme.qss`.
- Evaluar indicadores de progreso medible si los motores exponen esa información.

Deuda técnica que continúa vigente:

- Diagnosticar **DOC-001** (pérdida de contenido visual en una unión de PDF).
- Realizar más pruebas de rendimiento, fidelidad y archivos reales complejos.
- Evaluar cancelación segura de operaciones y recuperación frente a cierres forzosos.
- Evaluar empaquetado e instalador de Windows cuando las funcionalidades centrales estén estabilizadas.

## 9. Próxima etapa: nuevas funcionalidades

La siguiente fase prevista es ampliar las capacidades documentales de DocLab. Una idea prioritaria para evaluación es **Fotografías de clases → PDF**: importar varias imágenes, ordenarlas, corregir su orientación y generar un PDF local. Las mejoras avanzadas (perspectiva, recorte de diapositivas, limpieza de imagen y OCR opcional) requieren diseño y pruebas posteriores; no se presentan aquí como funciones ya implementadas.

El alcance exacto de la próxima etapa debe definirse antes de codificarla, manteniendo la arquitectura modular: **Interfaz → Trabajador (`QThread`) → Servicio → Motor documental**.

---

**DocLab — Convierte, organiza y transforma tus documentos.**