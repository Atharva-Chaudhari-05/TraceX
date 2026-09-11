import math
import tempfile
import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

from backend.app.analytics.ml_engine import MLEngine
from backend.app.analytics.model_registry import ModelRegistry

ORDERED_FEATURES = [
    "centrality_degree",
    "centrality_pagerank",
    "centrality_betweenness",
    "community_size",
    "tx_out_count",
    "tx_in_count",
    "comm_out_count",
    "comm_in_count",
    "unique_partners_count",
]

def _make_nodes(n, scenario_prefix="SCN-FIN"):
    return [
        {
            "id": f"N{i}",
            "labels": ["Person"],
            "properties": {"Generation_Batch_ID": f"{scenario_prefix}-{i:04d}"},
        }
        for i in range(n)
    ]

def _make_edges(nodes):
    edges = []
    ids = [n["id"] for n in nodes]
    for i in range(len(ids) - 1):
        edges.append(
            {
                "id": f"e{i}",
                "source": ids[i],
                "target": ids[i + 1],
                "type": "COMMUNICATES_WITH",
                "properties": {"Audit_Reference": f"REF-{i}"},
            }
        )
    return edges

def _make_feature_df(n_rows=10, seed=42):
    rng = np.random.default_rng(seed)
    data = rng.random((n_rows, len(ORDERED_FEATURES)))
    return pd.DataFrame(data, columns=ORDERED_FEATURES)

def _train_real_engine(tmp_path, n_samples=20, n_pos=10):
    engine = MLEngine()
    reg = ModelRegistry.__new__(ModelRegistry)
    reg.base_dir = tmp_path
    reg.base_dir.mkdir(parents=True, exist_ok=True)
    engine.registry = reg

    rng = np.random.default_rng(42)
    X_all = pd.DataFrame(rng.random((n_samples, len(ORDERED_FEATURES))), columns=ORDERED_FEATURES)
    y_all = pd.Series([1] * n_pos + [0] * (n_samples - n_pos))

    split = int(n_samples * 0.8)
    mock_dataset = {
        "X_train": X_all.iloc[:split],
        "y_train": y_all.iloc[:split],
        "X_val": X_all.iloc[split:],
        "y_val": y_all.iloc[split:],
        "target_name": "synthetic_dev_target",
        "target_version": "1.0",
        "fingerprint": "testfingerprint",
    }

    mock_db = MagicMock()
    mock_db.build_training_dataset.return_value = mock_dataset
    engine.dataset_builder = mock_db

    result = engine.train_models(["CASE_A", "CASE_B"])
    return engine, result, reg
