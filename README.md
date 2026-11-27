# Proyecto integrador de analítica de datos

Este repositorio reúne los avances del proyecto integrador realizados con el
dataset público `BIT/titanic-dataset` de Hugging Face. El trabajo está organizado
por actividad para conservar el historial y facilitar su revisión.

## Entrega AE4: métricas, visualización y aplicación de Streamlit

- **Documento final (PDF):** [`AE4 Proyecto integrador - Métricas y Visualización/documento/Proyecto_Integrado_III_Titanic_Santiago_Andres_Valencia_Duque.pdf`](<AE4 Proyecto integrador - Métricas y Visualización/documento/Proyecto_Integrado_III_Titanic_Santiago_Andres_Valencia_Duque.pdf>)
- **Aplicación de Streamlit:** `streamlit_app.py` (raíz del repositorio). Enlace público: *pendiente de publicar en Streamlit Community Cloud* (ver «Publicar la aplicación»).

### Ejecutar la aplicación

Desde la raíz del repositorio (Python 3.10 o superior):

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

La aplicación abre en `http://localhost:8501`. Tiene un menú superior con
Inicio (necesidad, preguntas y dataset), una página por pregunta (P1 a P5),
tarifas por clase, un explorador de segmentos con filtros, conclusiones y una
página de verificación. Cada pregunta muestra la ficha de la métrica (cálculo,
unidad y periodo), indicadores, gráficos interactivos, interpretación,
decisión que apoya, limitaciones y la tabla descargable en CSV.

### Datos que usa la aplicación

| Ruta | Uso |
|---|---|
| `AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/datos/titanic_preparado.csv` | Dataset preparado (891 filas, 9 columnas) del que se calculan todas las métricas |
| `AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/resultados/pregunta_*.csv` | Tablas del notebook de AE3 con las que se verifica que las cifras coincidan |
| `AE4 Proyecto integrador - Métricas y Visualización/src/metricas.py` | Cálculo único de métricas para la app, el notebook de AE4 y el documento |

No se descarga nada al abrir la app: los datos ya están en el repositorio.

### Métricas por pregunta

| Pregunta | Métrica | Cálculo | Unidad | Resultado principal |
|---|---|---|---|---|
| P1 Total | Tasa de supervivencia | sobrevivientes / pasajeros × 100 | % | 38,38 % (342 de 891) |
| P2 Clase | Tasa por clase y participación | sobrevivientes de la clase / pasajeros de la clase × 100 | % | Primera 62,96 %, Segunda 47,28 %, Tercera 24,24 % |
| P3 Sexo | Tasa por sexo y brecha | tasa mujeres − tasa hombres | %, p. p. | Mujeres 74,20 %, hombres 18,89 % (55,31 p. p.) |
| P4 Edad | Tasa por grupo de edad | sobrevivientes del grupo / pasajeros del grupo × 100 | % | 0 a 12 años 57,97 %; 60 o más 26,92 % |
| P5 Puerto | Tasa por puerto | sobrevivientes del puerto / pasajeros del puerto × 100 | % | Cherbourg 55,36 %, Southampton 33,70 % |
| Complemento | Participación en tarifa registrada | tarifa de la clase / tarifa total × 100 | % (moneda no indicada) | Primera: 24,24 % de pasajeros y 63,35 % de la tarifa |

La tarifa es un ingreso registrado, no rentabilidad (no hay costos). El análisis
es descriptivo: muestra asociaciones, no causas.

### Evidencias de AE4

| Evidencia | Ruta (dentro de la carpeta AE4) |
|---|---|
| Notebook ejecutado | `notebooks/metricas_visualizacion_titanic.ipynb` |
| Métricas y gráficos estáticos | `src/metricas.py`, `src/graficos.py`, `figuras/*.png` |
| Tablas complementarias y verificación | `resultados/complemento_*.csv`, `resultados/verificacion_cifras_ae3.csv` |
| Pruebas | `tests/test_metricas.py` |
| Documento final | `documento/*.docx` y `documento/*.pdf` |
| Guion de la presentación (10 min) | `presentacion/guion_video.md` |

### Regenerar notebook, documento y PDF

```bash
python -m pytest -q "AE4 Proyecto integrador - Métricas y Visualización/tests"
jupyter nbconvert --to notebook --execute --inplace "AE4 Proyecto integrador - Métricas y Visualización/notebooks/metricas_visualizacion_titanic.ipynb"
python "AE4 Proyecto integrador - Métricas y Visualización/src/generar_documento_final.py" [URL_DE_LA_APP]
powershell -ExecutionPolicy Bypass -File "AE4 Proyecto integrador - Métricas y Visualización/src/exportar_pdf.ps1" "AE4 Proyecto integrador - Métricas y Visualización/documento"
```

La exportación a PDF usa Microsoft Word (Windows).

### Publicar la aplicación

1. Entrar a https://share.streamlit.io con la cuenta de GitHub dueña del repositorio.
2. *Create app* → repositorio `andresvd95/PI3-ADD`, rama `main`, archivo `streamlit_app.py`.
3. Copiar el enlace generado en este README y en la plataforma.

## Avance AE3: transformación y enriquecimiento

Carpeta: `AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/`.
Parte del CSV de AE1 (`AE1/resultados/titanic_transformado.csv`), que viene del
split `train` de `BIT/titanic-dataset`, y conserva una copia sin modificar para
comparar el antes y el después.

### Transformaciones

- Tipos: `sobrevivio` y `clase_pasajero` pasan de `int64` a `int8`; `edad` y
  `tarifa` se convierten a numéricas.
- Validaciones: `sobrevivio` solo 0 o 1, `clase_pasajero` solo 1, 2 o 3 y sin
  edades ni tarifas negativas. Si una regla falla, la ejecución se detiene.
- Categorías: `sexo` pasa de `male`/`female` a `Hombre`/`Mujer` (891 registros).
- Faltantes: las 177 edades vacías se conservan como nulas y se marcan como
  `Edad no registrada` en `grupo_edad`; los 2 puertos vacíos pasan a `No registrado`.
- Duplicados: hay 120 filas con atributos coincidentes. No se eliminan porque el
  dataset no tiene identificador de pasajero.
- No se elimina ninguna fila: 891 registros antes y después, de 6 a 9 columnas.

### Enriquecimientos

| Variable | Regla |
|---|---|
| `estado_supervivencia` | 0 = No sobrevivió, 1 = Sobrevivió |
| `clase` | 1 = Primera, 2 = Segunda, 3 = Tercera |
| `grupo_edad` | Intervalos 0 a 12, 13 a 17, 18 a 29, 30 a 44, 45 a 59, 60 o más y Edad no registrada |

No se une ninguna otra tabla, por lo que no se pueden multiplicar registros.

### Preguntas de negocio abordadas

La pregunta compuesta de AE2 se dividió en cinco preguntas operativas:

1. ¿Cuál fue la supervivencia total registrada?
2. ¿Cómo varió según la clase?
3. ¿Cómo varió según el sexo?
4. ¿Cómo varió según el grupo de edad?
5. ¿Cómo varió según el puerto de embarque?

Cada tabla incluye pasajeros, sobrevivientes, no sobrevivientes, tasa de
supervivencia (%) y participación de pasajeros (%).

### Rutas de las evidencias

| Evidencia | Ruta (dentro de la carpeta AE3) |
|---|---|
| Notebook ejecutado | `notebooks/transformacion_enriquecimiento_titanic.ipynb` |
| Dataset preparado | `datos/titanic_preparado.csv` |
| Tablas de resultados | `resultados/pregunta_1_supervivencia_total.csv`, `resultados/pregunta_2_supervivencia_por_clase.csv`, `resultados/pregunta_3_supervivencia_por_sexo.csv`, `resultados/pregunta_4_supervivencia_por_grupo_edad.csv`, `resultados/pregunta_5_supervivencia_por_puerto.csv` |
| Resumen descriptivo `.txt` | `resultados/resumen_dataframe_ae3.txt` |
| Código | `src/transformar_titanic.py`, `src/generar_documento_ae3.py` |
| Pruebas | `tests/test_transformar_titanic.py` |
| Documento Word | `documento/AE3_Titanic.docx` |

El `.txt` lo genera el código a partir del DataFrame final y se reemplaza en cada
ejecución. Incluye filas, columnas, tipos, nulos y estadísticas descriptivas.

## Necesidad analítica de AE2

En un escenario académico hipotético, un equipo encargado de documentar la
seguridad marítima necesita conocer cómo se distribuyó la supervivencia observada
entre los pasajeros registrados según clase, sexo, edad y puerto de embarque. La
pregunta propuesta es: ¿cómo varió la proporción de supervivencia registrada entre
los grupos definidos por esas variables?

El proyecto es descriptivo. Los resultados permiten caracterizar asociaciones en
los registros, pero no demostrar que una característica haya causado la
supervivencia o el fallecimiento de una persona.

## Dataset

- Identificador: `BIT/titanic-dataset`
- Enlace: https://huggingface.co/datasets/BIT/titanic-dataset
- Split: `train`
- Registros: 891
- Variables: 15
- Licencia indicada en Hugging Face: Apache 2.0
- Fecha de consulta: 23 de octubre de 2026
- Muestra: no se utiliza; se procesa el split completo

La ficha de Hugging Face no explica la procedencia original ni indica si los datos
son sintéticos. Estas dos características quedan pendientes de confirmar con el
responsable del repositorio del dataset.

## Estructura

```text
AE1/
  notebooks/    Notebook de la primera actividad
  resultados/   Resumen y CSV generados automáticamente
  src/          Clases auxiliares
  tests/        Pruebas de las clases
AE2/
  documento/    Documento Word de AE2
  notebooks/    Carga y reconocimiento descriptivo del dataset
  resultados/   Resumen del DataFrame generado automáticamente
AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/
  datos/        Dataset preparado
  documento/    Documento Word de la entrega
  notebooks/    Notebook de transformación y enriquecimiento
  resultados/   Tablas por pregunta y resumen descriptivo
  src/          Scripts de transformación y de generación del documento
  tests/        Pruebas de la transformación
AE4 Proyecto integrador - Métricas y Visualización/
  documento/    Documento final del proyecto (Word y PDF)
  figuras/      Gráficos estáticos del documento
  notebooks/    Notebook de métricas y visualización
  resultados/   Tablas complementarias y verificación contra AE3
  src/          Métricas, gráficos y generación del documento
  tests/        Pruebas de las métricas
streamlit_app.py
.github/workflows/execute-notebook.yml
requirements.txt
```

## Ejecución local

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt   # pandas, datasets, jupyter, pytest y python-docx
jupyter nbconvert --to notebook --execute --inplace AE1/notebooks/actividad_titanic.ipynb
jupyter nbconvert --to notebook --execute --inplace AE2/notebooks/exploracion_titanic.ipynb
jupyter nbconvert --to notebook --execute --inplace "AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/notebooks/transformacion_enriquecimiento_titanic.ipynb" --ExecutePreprocessor.timeout=300
python -m pytest -q AE1/tests "AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/tests"
```

El notebook de AE3 usa rutas relativas, regenera los CSV y el TXT, y comprueba
que cada tabla conserve 891 pasajeros y 342 sobrevivientes. El proceso también
puede ejecutarse con `python "AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/src/transformar_titanic.py"`.
El Word se regenera con `python "AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos/src/generar_documento_ae3.py"`
y toma las cifras de los CSV exportados.

El segundo notebook crea `AE2/resultados/resumen_dataframe.txt` con el
identificador, el split, las dimensiones, los nombres y tipos de columnas y los
valores nulos del mismo DataFrame revisado en Jupyter.

## Automatización en GitHub

GitHub Actions ejecuta las pruebas y los notebooks de AE1, AE2 y AE3 en cada envío a `main`.
Después valida los resultados y, si cambiaron, `github-actions[bot]` los publica
mediante un commit automático. También deja un paquete descargable llamado
`actividades-titanic-ejecutadas` en la ejecución del workflow.
