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