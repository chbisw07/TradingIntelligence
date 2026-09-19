"""Bounded local JSON admission using FF-0's existing safe file reader.

No default paths, acquisition, CSV guessing, model persistence or command verbs.
Serialize contracts with forecasting.identity.canonical_json; reconstruction
validates the report seal. Storage/retention authorization is a separate gate.
"""

from pathlib import Path

from tiaf.evaluation.forecast_research_contracts import DailyBarInput, EmpiricalDataset
from tiaf.forecasting.engineering import _read_json


def load_research_dataset(path: Path, *, dataset_id: str) -> EmpiricalDataset:
    data = _read_json(path)
    # Supplied rows may carry unrelated source columns. Ignore only extra columns;
    # never rename fields, infer provenance, coerce corrupt values or relax the envelope.
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        data = {
            **data,
            "rows": [
                {k: v for k, v in row.items() if k in DailyBarInput.model_fields}
                if isinstance(row, dict)
                else row
                for row in data["rows"]
            ],
        }
    dataset = EmpiricalDataset.model_validate(data)
    if dataset.dataset_id != dataset_id:
        raise ValueError("RESEARCH_DATASET_ID_MISMATCH")
    return dataset
