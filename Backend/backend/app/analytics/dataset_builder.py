import logging
import hashlib
from typing import List, Tuple, Dict, Any
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from backend.app.graph.engine import GraphEngine
from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.targets import get_target_provider

logger = logging.getLogger(__name__)

class DatasetBuilder:
    def __init__(self):
        self.graph_engine = GraphEngine()
        self.feature_builder = FeatureBuilder()

    def build_training_dataset(
        self, case_ids: List[str], target_definition: str, test_size: float = 0.2, random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Builds the training and validation datasets across multiple cases.
        Performs deterministic group-aware splitting based on case_id.
        """
        if not case_ids:
            raise ValueError("No cases provided for training.")

        target_provider = get_target_provider(target_definition)

        all_features = []
        all_targets = []
        all_groups = []

        # We will iterate and build per-case to respect memory bounds
        for case_id in case_ids:
            try:
                # 1. Extract case subgraph
                # We fetch MAX + 1 to let GraphEngine and NetworkAnalyticsEngine limits apply if needed
                # Wait, the limits in M7 are 5000/20000. We pass those explicitly.
                subgraph = self.graph_engine.extract_case_subgraph(case_id, max_nodes=5000, max_edges=20000)
                nodes = subgraph["nodes"]
                edges = subgraph["edges"]

                if len(nodes) > 5000 or len(edges) > 20000:
                    raise ValueError(f"Case {case_id} exceeds resource limits (nodes: {len(nodes)}, edges: {len(edges)}).")

                if not nodes:
                    continue

                # 2. Build feature matrix (X)
                df_features = self.feature_builder.build_features(nodes, edges)

                # 3. Build targets (y)
                y_series = target_provider.compute_targets(nodes)

                # 4. Retain grouping by case
                # We align targets to the features explicitly
                df_features["_case_id"] = case_id
                df_features["_target"] = y_series

                all_features.append(df_features)

            except ValueError as ve:
                logger.error(f"Failed to process case {case_id}: {ve}")
                raise ve
            except Exception as e:
                logger.error(f"Unexpected error processing case {case_id}: {e}")
                raise RuntimeError(f"Dataset construction failed on case {case_id}")

        if not all_features:
            raise ValueError("No entities found across provided cases.")

        df_combined = pd.concat(all_features, axis=0)

        # Separate targets and groups from features
        groups = df_combined["_case_id"]
        y = df_combined["_target"]
        X = df_combined.drop(columns=["_case_id", "_target"])

        # Check if we have enough distinct cases for a valid split
        unique_cases = groups.nunique()
        if unique_cases <= 2 and test_size > 0:
            logger.warning(f"Only {unique_cases} case(s) available. Cannot perform group-aware split. Using all for training.")
            return {
                "X_train": X,
                "y_train": y,
                "X_val": None,
                "y_val": None,
                "target_name": target_provider.get_target_name(),
                "target_version": target_provider.get_target_version(),
                "fingerprint": self._generate_fingerprint(X)
            }

        # Deterministic Group-Aware Splitting
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_seed)
        train_idx, val_idx = next(gss.split(X, y, groups=groups))

        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        return {
            "X_train": X_train,
            "y_train": y_train,
            "X_val": X_val,
            "y_val": y_val,
            "target_name": target_provider.get_target_name(),
            "target_version": target_provider.get_target_version(),
            "fingerprint": self._generate_fingerprint(X)
        }
        
    def _generate_fingerprint(self, df: pd.DataFrame) -> str:
        """Generate a deterministic fingerprint for the dataset."""
        # Simple hash of index (entity_ids) + shape
        data_str = f"{df.shape}_{sorted(df.index.tolist())}"
        return hashlib.sha256(data_str.encode()).hexdigest()
