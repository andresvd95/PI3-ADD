from pathlib import Path
import sys

import pandas as pd

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from transformar_titanic import construir_resultados, transformar, validar_resultados


def datos_minimos():
    return pd.DataFrame(
        {
            "sobrevivio": [0, 1, 1],
            "clase_pasajero": [3, 1, 2],
            "sexo": ["male", "female", "female"],
            "edad": [22.0, None, 12.0],
            "tarifa": [7.25, 71.28, 10.0],
            "ciudad_embarque": ["Southampton", None, "Cherbourg"],
        }
    )


def test_transformacion_conserva_filas_y_faltantes_como_categoria():
    final, auditoria = transformar(datos_minimos())
    assert len(final) == 3
    assert auditoria["filas_eliminadas"] == 0
    assert "Edad no registrada" in set(final["grupo_edad"])
    assert "No registrado" in set(final["ciudad_embarque"])


def test_tablas_conservan_totales():
    final, _ = transformar(datos_minimos())
    tablas = construir_resultados(final)
    validar_resultados(final, tablas)
    assert all(tabla["pasajeros"].sum() == 3 for tabla in tablas.values())
