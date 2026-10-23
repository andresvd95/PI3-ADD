# Actividad 1: carga y preparación de datos

Este proyecto obtiene el dataset público `BIT/titanic-dataset` desde Hugging Face,
lo convierte en un DataFrame de pandas, aplica una transformación mínima y genera
un resumen descriptivo en formato de texto y un archivo CSV con los datos transformados.

## Archivos principales

- `hf_dataset_loader.py`: clase que descarga un split desde Hugging Face.
- `dataset_summarizer.py`: clase que resume un DataFrame y genera un archivo `.txt`.
- `actividad_titanic.ipynb`: notebook que coordina la carga, transformación y resumen.
- `resumen_titanic.txt`: resultado generado con el DataFrame transformado.
- `titanic_transformado.csv`: datos transformados, listos para abrir en una hoja de cálculo.
- `.github/workflows/execute-notebook.yml`: ejecución automática en GitHub Actions.

## Transformación realizada

El notebook selecciona seis variables relevantes del conjunto original y cambia
sus nombres al español. El nuevo DataFrame es el que se entrega a la clase
`DatasetSummarizer`, por lo que `resumen_titanic.txt` describe exactamente los
datos transformados.

## Ejecución local

```bash
python -m pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace actividad_titanic.ipynb
```

Al ejecutar el notebook desde su carpeta, se crean `resumen_titanic.txt` y
`titanic_transformado.csv` en esa misma carpeta.

También puede abrirse `actividad_titanic.ipynb` en Jupyter o VS Code y ejecutar
las celdas en orden.

## Ejecución automática

El workflow **Ejecutar actividad Titanic** se activa con cada cambio enviado a
`main`, en los pull requests y manualmente desde la pestaña **Actions**. Ejecuta
las pruebas, procesa el notebook y verifica los dos archivos. Para descargarlos,
abre la ejecución en **Actions** y selecciona `actividad-titanic-ejecutada` en
la sección **Artifacts**.
