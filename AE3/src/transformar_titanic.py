"""Transformación reproducible del dataset Titanic para la actividad AE3."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd


COLUMNAS_ENTRADA = [
    "sobrevivio",
    "clase_pasajero",
    "sexo",
    "edad",
    "tarifa",
    "ciudad_embarque",
]


def localizar_raiz(inicio: Path | None = None) -> Path:
    """Localiza la raíz del repositorio desde el directorio de ejecución."""
    actual = (inicio or Path.cwd()).resolve()
    for candidata in (actual, *actual.parents):
        if (candidata / "AE1" / "resultados" / "titanic_transformado.csv").exists():
            return candidata
    raise FileNotFoundError("No se encontró la raíz del proyecto ni el CSV de AE1.")


def cargar_datos(ruta: Path) -> pd.DataFrame:
    """Carga el dataset local y conserva un DataFrame independiente."""
    df = pd.read_csv(ruta)
    faltantes = set(COLUMNAS_ENTRADA) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")
    return df[COLUMNAS_ENTRADA].copy(deep=True)


def transformar(df_original: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Corrige tipos, normaliza categorías y crea variables derivadas."""
    df = df_original.copy(deep=True)
    antes_nulos = df.isna().sum()

    df["sobrevivio"] = pd.to_numeric(df["sobrevivio"], errors="raise").astype("int8")
    df["clase_pasajero"] = pd.to_numeric(df["clase_pasajero"], errors="raise").astype("int8")
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df["tarifa"] = pd.to_numeric(df["tarifa"], errors="coerce")

    if not df["sobrevivio"].isin([0, 1]).all():
        raise ValueError("La variable sobrevivio contiene valores distintos de 0 y 1.")
    if not df["clase_pasajero"].isin([1, 2, 3]).all():
        raise ValueError("La clase contiene valores fuera del rango 1 a 3.")
    if (df["edad"].dropna() < 0).any() or (df["tarifa"].dropna() < 0).any():
        raise ValueError("Se encontraron edades o tarifas negativas.")

    sexo_limpio = df["sexo"].astype("string").str.strip().str.lower()
    mapa_sexo = {"male": "Hombre", "female": "Mujer"}
    desconocidos = set(sexo_limpio.dropna().unique()) - set(mapa_sexo)
    if desconocidos:
        raise ValueError(f"Categorías de sexo no reconocidas: {sorted(desconocidos)}")
    df["sexo"] = sexo_limpio.map(mapa_sexo).fillna("No registrado")

    ciudad = df["ciudad_embarque"].astype("string").str.strip()
    df["ciudad_embarque"] = ciudad.fillna("No registrado").replace("", "No registrado")

    df["estado_supervivencia"] = df["sobrevivio"].map({0: "No sobrevivió", 1: "Sobrevivió"})
    df["clase"] = df["clase_pasajero"].map({1: "Primera", 2: "Segunda", 3: "Tercera"})
    cortes = [-float("inf"), 12, 17, 29, 44, 59, float("inf")]
    etiquetas = ["0 a 12", "13 a 17", "18 a 29", "30 a 44", "45 a 59", "60 o más"]
    grupo = pd.cut(df["edad"], bins=cortes, labels=etiquetas, right=True)
    df["grupo_edad"] = grupo.astype("string").fillna("Edad no registrada")

    auditoria = {
        "filas_antes": len(df_original),
        "filas_despues": len(df),
        "columnas_antes": df_original.shape[1],
        "columnas_despues": df.shape[1],
        "edades_no_registradas": int(antes_nulos["edad"]),
        "puertos_no_registrados": int(antes_nulos["ciudad_embarque"]),
        "coincidencias_en_seis_variables": int(df_original.duplicated().sum()),
        "filas_eliminadas": 0,
        "variables_incorporadas": 3,
    }
    return df, auditoria


def tabla_supervivencia(df: pd.DataFrame, variable: str, nombre: str) -> pd.DataFrame:
    """Resume conteos y tasa de supervivencia para una variable de agrupación."""
    tabla = (
        df.groupby(variable, dropna=False, observed=False)["sobrevivio"]
        .agg(pasajeros="size", sobrevivientes="sum")
        .reset_index()
        .rename(columns={variable: nombre})
    )
    tabla["no_sobrevivientes"] = tabla["pasajeros"] - tabla["sobrevivientes"]
    tabla["tasa_supervivencia_pct"] = tabla["sobrevivientes"] / tabla["pasajeros"] * 100
    tabla["participacion_pasajeros_pct"] = tabla["pasajeros"] / len(df) * 100
    return tabla


def construir_resultados(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construye una tabla por pregunta de negocio."""
    total = tabla_supervivencia(df.assign(total="Total"), "total", "grupo")
    tablas = {
        "pregunta_1_supervivencia_total": total,
        "pregunta_2_supervivencia_por_clase": tabla_supervivencia(df, "clase", "clase"),
        "pregunta_3_supervivencia_por_sexo": tabla_supervivencia(df, "sexo", "sexo"),
        "pregunta_4_supervivencia_por_grupo_edad": tabla_supervivencia(
            df, "grupo_edad", "grupo_edad"
        ),
        "pregunta_5_supervivencia_por_puerto": tabla_supervivencia(
            df, "ciudad_embarque", "puerto_embarque"
        ),
    }
    for tabla in tablas.values():
        tabla["tasa_supervivencia_pct"] = tabla["tasa_supervivencia_pct"].round(2)
        tabla["participacion_pasajeros_pct"] = tabla["participacion_pasajeros_pct"].round(2)
    return tablas


def validar_resultados(df: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    """Comprueba que cada tabla conserve totales y conteos del dataset final."""
    sobrevivientes = int(df["sobrevivio"].sum())
    for nombre, tabla in tablas.items():
        if int(tabla["pasajeros"].sum()) != len(df):
            raise AssertionError(f"El total de pasajeros no coincide en {nombre}.")
        if int(tabla["sobrevivientes"].sum()) != sobrevivientes:
            raise AssertionError(f"El total de sobrevivientes no coincide en {nombre}.")
        if (tabla["tasa_supervivencia_pct"] < 0).any() or (
            tabla["tasa_supervivencia_pct"] > 100
        ).any():
            raise AssertionError(f"Hay porcentajes fuera de rango en {nombre}.")


def generar_resumen(df: pd.DataFrame, auditoria: dict[str, int]) -> str:
    """Genera el TXT descriptivo solicitado a partir del DataFrame final."""
    estructura = pd.DataFrame(
        {
            "tipo_dato": df.dtypes.astype(str),
            "valores_nulos": df.isna().sum(),
            "valores_unicos": df.nunique(dropna=True),
        }
    )
    buffer = StringIO()
    df[["sobrevivio", "clase_pasajero", "edad", "tarifa"]].describe().to_string(buf=buffer)
    lineas = [
        "RESUMEN DEL DATAFRAME TRANSFORMADO Y ENRIQUECIDO",
        "================================================",
        "Dataset de origen: BIT/titanic-dataset, split train",
        "Archivo local de entrada: AE1/resultados/titanic_transformado.csv",
        f"Cantidad de filas: {df.shape[0]}",
        f"Cantidad de columnas: {df.shape[1]}",
        f"Filas eliminadas: {auditoria['filas_eliminadas']}",
        "",
        "COLUMNAS TIPOS VALORES NULOS Y VALORES UNICOS",
        "------------------------------------------------",
        estructura.to_string(),
        "",
        "ESTADISTICAS DESCRIPTIVAS PERTINENTES",
        "---------------------------------------",
        buffer.getvalue(),
        "",
        "CONTROLES DE CALIDAD",
        "--------------------",
        f"Edades no registradas conservadas: {auditoria['edades_no_registradas']}",
        f"Puertos no registrados categorizados: {auditoria['puertos_no_registrados']}",
        "Registros coincidentes en las seis variables de entrada: "
        f"{auditoria['coincidencias_en_seis_variables']}",
        "Criterio de duplicados: no se eliminaron porque el archivo no contiene un identificador "
        "de pasajero y la coincidencia de atributos no demuestra duplicidad del registro.",
    ]
    return "\n".join(lineas) + "\n"


def ejecutar(raiz: Path | None = None) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, int]]:
    """Ejecuta la transformación, valida y exporta todas las evidencias de AE3."""
    raiz = raiz or localizar_raiz()
    entrada = raiz / "AE1" / "resultados" / "titanic_transformado.csv"
    salida_datos = raiz / "AE3" / "datos"
    salida_resultados = raiz / "AE3" / "resultados"
    salida_datos.mkdir(parents=True, exist_ok=True)
    salida_resultados.mkdir(parents=True, exist_ok=True)

    original = cargar_datos(entrada)
    preparado, auditoria = transformar(original)
    tablas = construir_resultados(preparado)
    validar_resultados(preparado, tablas)

    preparado.to_csv(salida_datos / "titanic_preparado.csv", index=False, encoding="utf-8-sig")
    for nombre, tabla in tablas.items():
        tabla.to_csv(salida_resultados / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    (salida_resultados / "resumen_dataframe_ae3.txt").write_text(
        generar_resumen(preparado, auditoria), encoding="utf-8"
    )
    return preparado, tablas, auditoria


if __name__ == "__main__":
    final, resultados, control = ejecutar()
    print(f"AE3 generada: {len(final)} filas, {final.shape[1]} columnas y {len(resultados)} tablas.")
    print(control)
