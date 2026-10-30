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
