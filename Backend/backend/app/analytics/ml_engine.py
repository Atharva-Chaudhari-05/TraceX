import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix

from backend.app.analytics.dataset_builder import DatasetBuilder
from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.model_registry import ModelRegistry
from backend.app.graph.engine import GraphEngine

logger = logging.getLogger(__name__)

class MLEngine:
    def __init__(self):
        self.dataset_builder = DatasetBuilder()
        self.feature_builder = FeatureBuilder()
        self.registry = ModelRegistry()
        self.graph_engine = GraphEngine()

    def _verify_schema_compatibility(self, current_version: str, current_names: List[str], metadata: Dict[str, Any]):
        if metadata.get("feature_schema_version") != current_version:
            raise ValueError(
                f"Feature schema version mismatch. Model expects {metadata.get('feature_schema_version')}, "
                f"but current is {current_version}"
            )
        expected_names = metadata.get("ordered_feature_names", [])
        if expected_names != current_names:
            raise ValueError("Feature ordering mismatch between model metadata and current feature builder.")

    def train_models(self, case_ids: List[str], target_definition: str = "synthetic_dev_target_v1") -> Dict[str, Any]:
        """
        Orchestrates training of both XGBoost and Isolation Forest models.
        """
        logger.info(f"Starting M8 model training on {len(case_ids)} cases using {target_definition}")
        
        # 1. Build Dataset
        dataset_info = self.dataset_builder.build_training_dataset(case_ids, target_definition, test_size=0.2)
        X_train = dataset_info["X_train"]
        y_train = dataset_info["y_train"]
        X_val = dataset_info["X_val"]
        y_val = dataset_info["y_val"]
        
        feature_schema_version = self.feature_builder.feature_schema_version
        ordered_feature_names = self.feature_builder.ordered_feature_names

        # 2. Train XGBoost
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            eval_metric="logloss" # avoid warning
        )
        
        xgb_model.fit(X_train, y_train)

        # Evaluate XGBoost
        metrics = {}
        if X_val is not None and y_val is not None and len(np.unique(y_val)) > 1:
            y_pred = xgb_model.predict(X_val)
            y_prob = xgb_model.predict_proba(X_val)[:, 1]
            try:
                metrics["roc_auc"] = float(roc_auc_score(y_val, y_prob))
            except ValueError:
                metrics["roc_auc"] = None
            metrics["f1"] = float(f1_score(y_val, y_pred, zero_division=0))
            metrics["precision"] = float(precision_score(y_val, y_pred, zero_division=0))
            metrics["recall"] = float(recall_score(y_val, y_pred, zero_division=0))
            cm = confusion_matrix(y_val, y_pred).tolist()
            metrics["confusion_matrix"] = cm
        else:
            logger.warning("Validation set missing or single-class. Evaluation skipped.")
            metrics["warning"] = "Insufficient validation diversity for metrics"

        xgb_metadata = {
            "feature_schema_version": feature_schema_version,
            "ordered_feature_names": ordered_feature_names,
            "target_definition": dataset_info["target_name"],
            "target_version": dataset_info["target_version"],
            "training_dataset_fingerprint": dataset_info["fingerprint"],
            "hyperparameters": xgb_model.get_params(),
            "metrics": metrics,
            "training_group_split_strategy": "deterministic_by_case_id"
        }
        
        xgb_version = self.registry.save_xgboost_model(xgb_model, xgb_metadata)

        # 3. Train Isolation Forest
        # Scaler and IsolationForest are fitted ONLY on training data to prevent
        # validation-set distribution from leaking into the unsupervised model.
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        iso_model = IsolationForest(
            n_estimators=100,
            contamination="auto",
            random_state=42
        )
        iso_model.fit(X_train_scaled)

        iso_metadata = {
            "feature_schema_version": feature_schema_version,
            "ordered_feature_names": ordered_feature_names,
            "training_dataset_fingerprint": dataset_info["fingerprint"],
            "hyperparameters": {
                "n_estimators": 100,
                "contamination": "auto",
                "random_state": 42
            },
            "preprocessing": "StandardScaler"
        }
        
        iso_version = self.registry.save_isolation_forest_model(iso_model, scaler, iso_metadata)

        return {
            "status": "success",
            "xgboost_version": xgb_version,
            "isolation_forest_version": iso_version,
            "metrics": metrics
        }

    def _generate_explanation(self, xgb_prob: float, is_anomaly: bool, top_features: list) -> str:
        """
        Generates a concise, investigator-readable signal description.
        Uses appropriate analytical language — does not assert criminal guilt.
        """
        top_str = ", ".join(top_features[:3]) if top_features else "N/A"
        parts = []

        if xgb_prob >= 0.7:
            parts.append(f"High-risk development signal (XGBoost probability={xgb_prob:.2f})")
        elif xgb_prob >= 0.4:
            parts.append(f"Moderate development signal (XGBoost probability={xgb_prob:.2f})")
        else:
            parts.append(f"Low development signal (XGBoost probability={xgb_prob:.2f})")

        if is_anomaly:
            parts.append("anomalous structural pattern detected")
        else:
            parts.append("within-distribution structural pattern")

        if top_features:
            parts.append(f"primary contributing features: {top_str}")

        parts.append("Requires investigator review. "
                     "Synthetic development target - not real-world criminal ground truth.")

        return ". ".join(parts) + "."

    def infer_case(self, case_id: str) -> Dict[str, Any]:
        """
        Extracts case, builds features, loads models, and infers analytical signals.
        Returns structured, explainable per-entity signals.
        """
        # 1. Extract and build features
        subgraph = self.graph_engine.extract_case_subgraph(case_id, max_nodes=5000, max_edges=20000)
        nodes = subgraph["nodes"]
        edges = subgraph["edges"]

        if len(nodes) > 5000 or len(edges) > 20000:
            raise ValueError("Payload Too Large: Graph exceeds resource bounds.")

        df_features = self.feature_builder.build_features(nodes, edges)
        if df_features.empty:
            return {
                "case_id": case_id,
                "signals": [],
                "metadata": {}
            }

        # 2. Load models
        xgb_model, xgb_meta = self.registry.load_xgboost_model()
        iso_model, iso_scaler, iso_meta = self.registry.load_isolation_forest_model()

        # 3. Verify feature schema compatibility
        current_version = self.feature_builder.feature_schema_version
        current_names = self.feature_builder.ordered_feature_names

        self._verify_schema_compatibility(current_version, current_names, xgb_meta)
        self._verify_schema_compatibility(current_version, current_names, iso_meta)

        # Ensure df_features exactly matches the frozen order before inference
        X_infer = df_features[current_names]

        # 4. XGBoost inference
        xgb_probs = xgb_model.predict_proba(X_infer)[:, 1]

        # 5. Feature importance — for explainability
        # Importance is per-feature; multiply by absolute feature value for per-entity contribution.
        xgb_importances = np.array(xgb_model.feature_importances_)  # shape (n_features,)

        # 6. IsolationForest inference using persisted scaler (fitted on training data only)
        X_scaled = iso_scaler.transform(X_infer)
        iso_preds = iso_model.predict(X_scaled)   # 1=inlier, -1=outlier
        iso_scores = iso_model.decision_function(X_scaled)  # lower = more anomalous

        # 7. Build structured, explainable signals
        signals = []
        entity_ids = X_infer.index.tolist()
        feature_names = list(X_infer.columns)

        for i, eid in enumerate(entity_ids):
            frow = X_infer.iloc[i].to_dict()
            frow_arr = np.array([frow[f] for f in feature_names])

            # Top features: rank by importance × |feature value| for this entity
            contributions = xgb_importances * np.abs(frow_arr)
            top_idx = np.argsort(contributions)[::-1][:3]  # top 3
            top_feats = [feature_names[j] for j in top_idx if contributions[j] > 0]

            xgb_prob = float(xgb_probs[i])
            is_anomaly = bool(iso_preds[i] == -1)

            signals.append({
                "entity_id": eid,
                "xgboost_probability": xgb_prob,
                "is_anomaly": is_anomaly,
                "anomaly_score": float(iso_scores[i]),
                "feature_values": {k: (None if pd.isna(v) else float(v)) for k, v in frow.items()},
                "top_features": top_feats,
                "explanation": self._generate_explanation(xgb_prob, is_anomaly, top_feats),
            })

        return {
            "case_id": case_id,
            "signals": signals,
            "metadata": {
                "xgboost_version": xgb_meta["model_version"],
                "isolation_forest_version": iso_meta["model_version"],
                "feature_schema_version": current_version,
                "target_definition": xgb_meta.get("target_definition"),
                "synthetic_target_disclaimer": (
                    "Target is synthetic development labeling only. "
                    "Scores do not constitute criminal findings."
                ),
            },
        }
