"""Métricas de AE4 calculadas a partir del dataset preparado en AE3.

El módulo es la única fuente de cifras para el notebook, la aplicación de
Streamlit y el documento final. Recalcula las tablas de las cinco preguntas
desde ``titanic_preparado.csv`` y comprueba que coincidan con los CSV que
exportó el notebook de AE3.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

CARPETA_AE3 = "AE3 Proyecto integrador - Transformación y Enriquecimiento de Datos"
CARPETA_AE4 = "AE4 Proyecto integrador - Métricas y Visualización"

ORDEN = {
    "clase": ["Primera", "Segunda", "Tercera"],
    "sexo": ["Mujer", "Hombre"],
    "grupo_edad": [
        "0 a 12",
        "13 a 17",
        "18 a 29",
        "30 a 44",
        "45 a 59",
        "60 o más",
        "Edad no registrada",
    ],
    "puerto_embarque": ["Cherbourg", "Queenstown", "Southampton", "No registrado"],
}

# Pregunta -> (variable del dataset, nombre de la columna de grupo en la tabla)
PREGUNTAS = {
    "pregunta_1_supervivencia_total": (None, "grupo"),
    "pregunta_2_supervivencia_por_clase": ("clase", "clase"),
    "pregunta_3_supervivencia_por_sexo": ("sexo", "sexo"),
    "pregunta_4_supervivencia_por_grupo_edad": ("grupo_edad", "grupo_edad"),
    "pregunta_5_supervivencia_por_puerto": ("ciudad_embarque", "puerto_embarque"),
}

COLUMNAS_RESULTADO = [
    "pasajeros",
    "sobrevivientes",
    "no_sobrevivientes",
    "tasa_supervivencia_pct",
    "participacion_pasajeros_pct",
]


def localizar_raiz(inicio: Path | None = None) -> Path:
    """Busca la raíz del repositorio subiendo desde ``inicio`` o desde este archivo."""
    puntos = [inicio] if inicio else [Path.cwd(), Path(__file__)]
    for punto in puntos:
        actual = punto.resolve()
        for candidata in (actual, *actual.parents):
            if (candidata / CARPETA_AE3 / "datos" / "titanic_preparado.csv").exists():
                return candidata
    raise FileNotFoundError("No se encontró el dataset preparado de AE3.")


def cargar_preparado(raiz: Path) -> pd.DataFrame:
    """Lee el dataset preparado de AE3 (891 filas, 9 columnas)."""
    df = pd.read_csv(raiz / CARPETA_AE3 / "datos" / "titanic_preparado.csv", encoding="utf-8-sig")
    if df.shape != (891, 9):
        raise ValueError(f"El dataset preparado tiene una forma inesperada: {df.shape}")
    return df


def cargar_resultados_ae3(raiz: Path) -> dict[str, pd.DataFrame]:
    """Lee las cinco tablas de resultados exportadas por el notebook de AE3."""
    carpeta = raiz / CARPETA_AE3 / "resultados"
    return {
        nombre: pd.read_csv(carpeta / f"{nombre}.csv", encoding="utf-8-sig")
        for nombre in PREGUNTAS
    }


def _ordenar(tabla: pd.DataFrame, columna: str) -> pd.DataFrame:
    if columna not in ORDEN:
        return tabla.reset_index(drop=True)
    tabla = tabla.copy()
    tabla[columna] = pd.Categorical(tabla[columna], categories=ORDEN[columna], ordered=True)
    tabla = tabla.sort_values(columna).reset_index(drop=True)
    tabla[columna] = tabla[columna].astype(str)
    return tabla


def tabla_supervivencia(df: pd.DataFrame, variable: str, nombre: str) -> pd.DataFrame:
    """Pasajeros, sobrevivientes, tasa (%) y participación (%) por grupo."""
    tabla = (
        df.groupby(variable, dropna=False)["sobrevivio"]
        .agg(pasajeros="size", sobrevivientes="sum")
        .reset_index()
        .rename(columns={variable: nombre})
    )
    tabla["no_sobrevivientes"] = tabla["pasajeros"] - tabla["sobrevivientes"]
    tabla["tasa_supervivencia_pct"] = (tabla["sobrevivientes"] / tabla["pasajeros"] * 100).round(2)
    tabla["participacion_pasajeros_pct"] = (tabla["pasajeros"] / len(df) * 100).round(2)
    return _ordenar(tabla, nombre)


def tablas_preguntas(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Una tabla por pregunta de negocio, en el orden lógico de cada variable."""
    tablas = {}
    for nombre, (variable, columna) in PREGUNTAS.items():
        if variable is None:
            tablas[nombre] = tabla_supervivencia(df.assign(total="Total"), "total", columna)
        else:
            tablas[nombre] = tabla_supervivencia(df, variable, columna)
    return tablas


def tabla_clase_sexo(df: pd.DataFrame) -> pd.DataFrame:
    """Lectura conjunta de clase y sexo (complemento descriptivo de P2 y P3)."""
    tabla = (
        df.groupby(["clase", "sexo"])["sobrevivio"]
        .agg(pasajeros="size", sobrevivientes="sum")
        .reset_index()
    )
    tabla["tasa_supervivencia_pct"] = (tabla["sobrevivientes"] / tabla["pasajeros"] * 100).round(2)
    tabla["clase"] = pd.Categorical(tabla["clase"], ORDEN["clase"], ordered=True)
    tabla["sexo"] = pd.Categorical(tabla["sexo"], ORDEN["sexo"], ordered=True)
    tabla = tabla.sort_values(["clase", "sexo"]).reset_index(drop=True)
    tabla[["clase", "sexo"]] = tabla[["clase", "sexo"]].astype(str)
    return tabla


def tabla_tarifas(df: pd.DataFrame) -> pd.DataFrame:
    """Tarifa registrada por clase.

    La suma de tarifas es un ingreso por pasajes registrado (moneda no indicada);
    no es rentabilidad porque el dataset no tiene costos.
    """
    tabla = (
        df.groupby("clase")["tarifa"]
        .agg(
            pasajeros="size",
            tarifa_total="sum",
            tarifa_media="mean",
            tarifa_mediana="median",
            pasajes_tarifa_cero=lambda s: int((s == 0).sum()),
        )
        .reset_index()
    )
    tabla["participacion_tarifa_pct"] = (tabla["tarifa_total"] / df["tarifa"].sum() * 100).round(2)
    tabla["participacion_pasajeros_pct"] = (tabla["pasajeros"] / len(df) * 100).round(2)
    for col in ("tarifa_total", "tarifa_media", "tarifa_mediana"):
        tabla[col] = tabla[col].round(2)
    return _ordenar(tabla, "clase")


def verificar_contra_ae3(
    tablas: dict[str, pd.DataFrame], ae3: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Compara grupo a grupo las tablas recalculadas con los CSV de AE3."""
    filas = []
    for nombre, (_, columna) in PREGUNTAS.items():
        nueva = tablas[nombre].set_index(columna)[COLUMNAS_RESULTADO].sort_index()
        previa = ae3[nombre].set_index(columna)[COLUMNAS_RESULTADO].sort_index()
        mismos_grupos = list(nueva.index) == list(previa.index)
        coinciden = mismos_grupos and bool(((nueva - previa).abs() < 0.005).all().all())
        filas.append(
            {
                "tabla": nombre,
                "grupos": len(nueva),
                "pasajeros": int(nueva["pasajeros"].sum()),
                "sobrevivientes": int(nueva["sobrevivientes"].sum()),
                "coincide_con_ae3": coinciden,
            }
        )
    return pd.DataFrame(filas)


def calcular_todo(raiz: Path | None = None) -> dict[str, object]:
    """Carga los datos y devuelve todas las tablas y la verificación."""
    raiz = raiz or localizar_raiz()
    df = cargar_preparado(raiz)
    tablas = tablas_preguntas(df)
    return {
        "raiz": raiz,
        "datos": df,
        "tablas": tablas,
        "clase_sexo": tabla_clase_sexo(df),
        "tarifas": tabla_tarifas(df),
        "verificacion": verificar_contra_ae3(tablas, cargar_resultados_ae3(raiz)),
    }


def exportar(resultado: dict[str, object]) -> Path:
    """Guarda las tablas complementarias y la verificación en la carpeta de resultados de AE4."""
    salida = Path(resultado["raiz"]) / CARPETA_AE4 / "resultados"
    salida.mkdir(parents=True, exist_ok=True)
    archivos = {
        "complemento_supervivencia_clase_sexo.csv": resultado["clase_sexo"],
        "complemento_tarifas_por_clase.csv": resultado["tarifas"],
        "verificacion_cifras_ae3.csv": resultado["verificacion"],
    }
    for nombre, tabla in archivos.items():
        tabla.to_csv(salida / nombre, index=False, encoding="utf-8-sig")
    return salida


if __name__ == "__main__":
    res = calcular_todo()
    print(res["verificacion"].to_string(index=False))
    print(f"Tablas exportadas en: {exportar(res)}")
