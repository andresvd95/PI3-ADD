# Proyecto integrador de analítica de datos

Este repositorio reúne los avances del proyecto integrador realizados con el
dataset público `BIT/titanic-dataset` de Hugging Face. El trabajo está organizado
por actividad para conservar el historial y facilitar su revisión.

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
  documento/    Documento Word para entrega separada, excluido de Git
  notebooks/    Carga y reconocimiento descriptivo del dataset
  resultados/   Resumen del DataFrame generado automáticamente
.github/workflows/execute-notebook.yml
requirements.txt
```

## Ejecución local

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace AE1/notebooks/actividad_titanic.ipynb
jupyter nbconvert --to notebook --execute --inplace AE2/notebooks/exploracion_titanic.ipynb
```

El segundo notebook crea `AE2/resultados/resumen_dataframe.txt` con el
identificador, el split, las dimensiones, los nombres y tipos de columnas y los
valores nulos del mismo DataFrame revisado en Jupyter.

## Automatización en GitHub

GitHub Actions ejecuta las pruebas y ambos notebooks en cada envío a `main`.
Después valida los resultados y, si cambiaron, `github-actions[bot]` los publica
mediante un commit automático. También deja un paquete descargable llamado
`actividades-titanic-ejecutadas` en la ejecución del workflow.

El documento de AE2 se conserva únicamente en `AE2/documento/` en el equipo local
porque se adjunta por separado en la plataforma académica.
