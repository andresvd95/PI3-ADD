"""Carga de datasets de Hugging Face como DataFrames de pandas."""

from typing import Any

import pandas as pd
from datasets import load_dataset


class HFDatasetLoader:
    """Carga un dataset público de Hugging Face y lo convierte en DataFrame."""

    def __init__(
        self,
        dataset_id: str,
        split: str = "train",
        config_name: str | None = None,
        **load_options: Any,
    ) -> None:
        if not dataset_id.strip():
            raise ValueError("El identificador del dataset no puede estar vacío.")
        if not split.strip():
            raise ValueError("El split no puede estar vacío.")

        self.dataset_id = dataset_id
        self.split = split
        self.config_name = config_name
        self.load_options = load_options

    def load(self) -> pd.DataFrame:
        """Descarga el split configurado y devuelve una copia como DataFrame."""
        dataset = load_dataset(
            self.dataset_id,
            self.config_name,
            split=self.split,
            **self.load_options,
        )
        return dataset.to_pandas().copy()
