"""Generación de resúmenes descriptivos para DataFrames."""

from pathlib import Path

import pandas as pd


class DatasetSummarizer:
    """Construye y guarda un resumen de un DataFrame en formato de texto."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Se debe proporcionar un DataFrame de pandas.")
        self.dataframe = dataframe.copy()

    def build_summary(self) -> str:
        """Devuelve un resumen legible de estructura, nulos y estadísticas."""
        rows, columns = self.dataframe.shape
        column_details = pd.DataFrame(
            {
                "tipo": self.dataframe.dtypes.astype(str),
                "valores_nulos": self.dataframe.isna().sum(),
                "porcentaje_nulos": (
                    self.dataframe.isna().mean().mul(100).round(2)
                ),
            }
        )

        sections = [
            "RESUMEN DEL DATASET TRANSFORMADO",
            "================================",
            f"Cantidad de filas: {rows}",
            f"Cantidad de columnas: {columns}",
            "",
            "COLUMNAS, TIPOS Y VALORES NULOS",
            "--------------------------------",
            column_details.to_string(),
            "",
            "ESTADÍSTICAS DESCRIPTIVAS",
            "-------------------------",
            self.dataframe.describe(include="all").transpose().to_string(),
        ]
        return "\n".join(sections) + "\n"

    def save(self, output_path: str | Path) -> Path:
        """Guarda el resumen en UTF-8 y devuelve la ruta generada."""
        path = Path(output_path)
        if path.suffix.lower() != ".txt":
            raise ValueError("El archivo de salida debe tener extensión .txt.")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.build_summary(), encoding="utf-8")
        return path
