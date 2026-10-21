import pandas as pd
import pytest

import hf_dataset_loader
from hf_dataset_loader import HFDatasetLoader


class FakeDataset:
    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame({"survived": [0, 1], "age": [22.0, 38.0]})


def test_load_returns_dataframe(monkeypatch: pytest.MonkeyPatch) -> None:
    received: dict[str, object] = {}

    def fake_load_dataset(
        dataset_id: str,
        config_name: str | None,
        **options: object,
    ) -> FakeDataset:
        received.update(
            dataset_id=dataset_id,
            config_name=config_name,
            options=options,
        )
        return FakeDataset()

    monkeypatch.setattr(hf_dataset_loader, "load_dataset", fake_load_dataset)

    dataframe = HFDatasetLoader("BIT/titanic-dataset", split="train").load()

    assert isinstance(dataframe, pd.DataFrame)
    assert dataframe.shape == (2, 2)
    assert received["dataset_id"] == "BIT/titanic-dataset"
    assert received["options"] == {"split": "train"}


@pytest.mark.parametrize("dataset_id", ["", "   "])
def test_rejects_empty_dataset_id(dataset_id: str) -> None:
    with pytest.raises(ValueError, match="identificador"):
        HFDatasetLoader(dataset_id)
