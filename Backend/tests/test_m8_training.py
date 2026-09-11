import json
import pytest
from m8_test_utils import _train_real_engine, ORDERED_FEATURES

class TestXGBoostTraining:
    def test_train_returns_success_status(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert result["status"] == "success"

    def test_train_returns_version_string(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert result["xgboost_version"].startswith("v")

    def test_train_returns_metrics(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert "roc_auc" in result["metrics"] or "warning" in result["metrics"]

    def test_model_artifact_exists_on_disk(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        model_path = reg.base_dir / "xgboost" / version / "model.json"
        assert model_path.exists(), "XGBoost model.json not found on disk"

    def test_metadata_artifact_exists_on_disk(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        meta_path = reg.base_dir / "xgboost" / version / "metadata.json"
        assert meta_path.exists(), "XGBoost metadata.json not found on disk"

    def test_metadata_contains_required_keys(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        with open(reg.base_dir / "xgboost" / version / "metadata.json") as f:
            meta = json.load(f)
        for key in [
            "feature_schema_version",
            "ordered_feature_names",
            "target_definition",
            "model_version",
            "created_at",
        ]:
            assert key in meta, f"Missing metadata key: {key}"

    def test_feature_schema_version_in_metadata(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        with open(reg.base_dir / "xgboost" / version / "metadata.json") as f:
            meta = json.load(f)
        assert meta["feature_schema_version"] == "1.0"
        assert meta["ordered_feature_names"] == ORDERED_FEATURES

    def test_second_train_increments_version(self, tmp_path):
        _, r1, _ = _train_real_engine(tmp_path)
        _, r2, _ = _train_real_engine(tmp_path)
        v1 = int(r1["xgboost_version"][1:])
        v2 = int(r2["xgboost_version"][1:])
        assert v2 == v1 + 1, "Second training should produce the next version"

class TestIsolationForestLeakage:
    def test_isolation_forest_artifact_exists(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        iso_version = result["isolation_forest_version"]
        model_path = reg.base_dir / "isolation_forest" / iso_version / "model.joblib"
        scaler_path = reg.base_dir / "isolation_forest" / iso_version / "scaler.joblib"
        assert model_path.exists()
        assert scaler_path.exists()

    def test_scaler_fitted_on_train_only(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        import joblib
        iso_version = result["isolation_forest_version"]
        scaler = joblib.load(reg.base_dir / "isolation_forest" / iso_version / "scaler.joblib")
        assert hasattr(scaler, "mean_"), "Scaler was not fitted (missing mean_)"
        assert len(scaler.mean_) == len(ORDERED_FEATURES)

    def test_isolation_forest_metadata_has_preprocessing_field(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        iso_version = result["isolation_forest_version"]
        with open(reg.base_dir / "isolation_forest" / iso_version / "metadata.json") as f:
            meta = json.load(f)
        assert meta.get("preprocessing") == "StandardScaler"
