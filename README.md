# Asesor Financiero OED

Herramienta de análisis y asesoría financiera construida sobre **notebooks de Python (Jupyter)**.
El proyecto ingesta datos financieros, los limpia y valida, ejecuta análisis y cálculos, y genera
recomendaciones y reportes accionables para apoyar la toma de decisiones.

> **Nota:** Este README describe la **arquitectura objetivo (propuesta)** del proyecto. El
> repositorio parte vacío, por lo que este documento sirve como guía de referencia para estructurar
> el desarrollo. Las rutas del árbol de directorios son ilustrativas y se irán creando a medida que
> avance el proyecto.

---

## Visión general de la arquitectura

La arquitectura es **notebook-céntrica**: los notebooks de Jupyter actúan como un *pipeline* de
etapas (ingesta → limpieza → análisis → recomendaciones → reporte), mientras que la lógica
reutilizable y testeable vive en módulos Python dentro de `src/`. Los datos fluyen de forma
unidireccional desde fuentes crudas hasta salidas/reportes, pasando por carpetas intermedias.

Principios clave:

- **Notebooks = exploración y orquestación.** Cuentan la "historia" del análisis paso a paso.
- **`src/` = código reutilizable.** Funciones de carga, cálculos financieros y utilidades, fáciles
  de importar, versionar y probar. Evita duplicar lógica entre notebooks.
- **Datos fuera del control de versiones.** Los datos crudos y procesados no se versionan (ver
  `.gitignore`); solo el código y la configuración.
- **Flujo unidireccional.** Cada etapa consume la salida de la anterior, lo que hace el proceso
  reproducible y fácil de depurar.

---

## Diagrama de capas

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA DE DATOS                                                │
│  data/raw/  ──►  data/processed/                              │
│  (fuentes crudas: CSV, Excel, extractos)  (datos limpios)    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA DE PROCESAMIENTO (notebooks/)                          │
│  00-ingesta ► 01-limpieza ► 02-análisis ► 03-recomendaciones │
│             ► 04-reportes                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │   importa funciones de
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA DE LÓGICA REUTILIZABLE (src/)                          │
│  carga de datos · cálculos financieros · utilidades · config │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA DE SALIDAS (outputs/)                                  │
│  gráficos · tablas · reportes (PDF/HTML/Excel)               │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura de directorios propuesta

```
asesor_financiero_oed/
├── data/
│   ├── raw/                 # Datos de entrada sin modificar (no versionados)
│   └── processed/           # Datos limpios y transformados (no versionados)
│
├── notebooks/               # Pipeline de análisis, numerado por etapa
│   ├── 00_ingesta.ipynb           # Carga de fuentes de datos
│   ├── 01_limpieza.ipynb          # Limpieza y validación
│   ├── 02_analisis.ipynb          # Análisis y cálculos financieros
│   ├── 03_recomendaciones.ipynb   # Generación de recomendaciones
│   └── 04_reportes.ipynb          # Construcción de reportes finales
│
├── src/                     # Código Python reutilizable
│   ├── __init__.py
│   ├── data_loader.py             # Funciones de carga/lectura de datos
│   ├── finance.py                 # Cálculos financieros (ratios, proyecciones, etc.)
│   ├── utils.py                   # Utilidades generales
│   └── reporting.py               # Generación de gráficos y reportes
│
├── outputs/                 # Resultados generados (gráficos, tablas, reportes)
│
├── config/                  # Parámetros y configuración del proyecto
│   └── config.yaml
│
├── requirements.txt         # Dependencias (o environment.yml para conda)
├── .gitignore               # Excluye data/, outputs/, entornos, checkpoints
└── README.md
```

---

## Flujo de datos (pipeline)

Los notebooks se ejecutan en orden y cada uno consume la salida del anterior:

1. **`00_ingesta`** — Lee las fuentes crudas desde `data/raw/` (CSV, Excel, extractos bancarios,
   estados financieros) usando funciones de `src/data_loader.py`.
2. **`01_limpieza`** — Normaliza tipos, maneja valores faltantes, valida consistencia y deja datos
   limpios en `data/processed/`.
3. **`02_analisis`** — Calcula indicadores financieros (ratios, flujos, rentabilidad, riesgo,
   proyecciones) apoyándose en `src/finance.py`.
4. **`03_recomendaciones`** — Aplica reglas y criterios de negocio sobre los resultados del análisis
   para producir recomendaciones de asesoría.
5. **`04_reportes`** — Compone gráficos y tablas (`src/reporting.py`) y exporta los reportes finales
   a `outputs/`.

```
data/raw  ──►  00_ingesta  ──►  01_limpieza  ──►  data/processed
                                                       │
                                                       ▼
outputs  ◄──  04_reportes  ◄──  03_recomendaciones  ◄──  02_analisis
```

---

## Componentes principales

| Componente              | Responsabilidad                                                        |
|-------------------------|------------------------------------------------------------------------|
| `data/raw/`             | Fuente de verdad de los datos de entrada, sin modificar.               |
| `data/processed/`       | Datos limpios y listos para analizar.                                  |
| `notebooks/`            | Orquestación del pipeline y narrativa del análisis, etapa por etapa.   |
| `src/data_loader.py`    | Lectura y carga estandarizada de las distintas fuentes de datos.       |
| `src/finance.py`        | Lógica de cálculos e indicadores financieros reutilizable.             |
| `src/reporting.py`      | Generación de visualizaciones y reportes.                              |
| `src/utils.py`          | Funciones auxiliares transversales.                                    |
| `config/`               | Parámetros del proyecto (rutas, umbrales, supuestos) centralizados.    |
| `outputs/`              | Productos finales: gráficos, tablas y reportes.                        |

---

## Stack tecnológico

- **Lenguaje:** Python 3
- **Entorno de trabajo:** Jupyter Notebook / JupyterLab
- **Librerías recomendadas** (a ajustar según necesidad):
  - `pandas`, `numpy` — manipulación y cálculo de datos.
  - `matplotlib` / `plotly` — visualización.
  - `openpyxl` — lectura/escritura de archivos Excel.
  - `pyyaml` — carga de configuración.

> Las versiones no se fijan en este documento; se definirán en `requirements.txt` (o
> `environment.yml`) cuando se inicialice el entorno.

---

## Cómo empezar

```bash
# 1. Crear y activar un entorno virtual
python3 -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar Jupyter
jupyter lab                         # o: jupyter notebook
```

Luego ejecuta los notebooks de `notebooks/` **en orden** (`00` → `04`). Coloca los datos de entrada
en `data/raw/` antes de correr `00_ingesta`.

---

## Convenciones

- **Numeración de notebooks.** El prefijo (`00_`, `01_`, …) indica el orden de ejecución del pipeline.
- **Notebook vs. `src/`.** Los notebooks exploran y orquestan; el código que se reutiliza o necesita
  pruebas se mueve a `src/` y se importa. Evita duplicar lógica entre notebooks.
- **Datos fuera de Git.** `data/` y `outputs/` se excluyen del control de versiones mediante
  `.gitignore`. Solo se versiona código y configuración.
- **Configuración centralizada.** Rutas, umbrales y supuestos viven en `config/`, no incrustados en
  los notebooks.
- **Reproducibilidad.** Ejecuta los notebooks de principio a fin ("Restart & Run All") antes de
  considerar un resultado válido.
