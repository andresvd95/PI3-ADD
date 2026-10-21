from pathlib import Path

import pandas as pd
import pytest

from dataset_summarizer import DatasetSummarizer


def test_build_summary_includes_shape_columns_and_nulls() -> None:
    dataframe = pd.DataFrame(
        {
            "edad": [22.0, None, 38.0],
            "sobrevivio": [0, 1, 1],
        }
    )

    summary = DatasetSummarizer(dataframe).build_summary()

    assert "Cantidad de filas: 3" in summary
    assert "Cantidad de columnas: 2" in summary
    assert "edad" in summary
    assert "float64" in summary
    assert "1" in summary


def test_save_writes_utf8_text_file(tmp_path: Path) -> None:
    dataframe = pd.DataFrame({"clase": [1, 2, 3]})
    output_path = tmp_path / "resumen.txt"

    result = DatasetSummarizer(dataframe).save(output_path)

    assert result == output_path
    assert output_path.read_text(encoding="utf-8").startswith(
        "RESUMEN DEL DATASET TRANSFORMADO"
    )


def test_save_rejects_non_text_extension(tmp_path: Path) -> None:
    summarizer = DatasetSummarizer(pd.DataFrame({"clase": [1]}))

    with pytest.raises(ValueError, match="extensión .txt"):
        summarizer.save(tmp_path / "resumen.csv")
