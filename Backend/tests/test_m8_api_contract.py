import pytest

class TestApiContract:
    def test_train_request_model_defaults(self):
        from backend.app.analytics.models import MLTrainRequest
        req = MLTrainRequest(case_ids=["C1", "C2"])
        assert req.target_definition == "synthetic_dev_target_v1"

    def test_ml_signal_optional_fields(self):
        from backend.app.analytics.models import MLSignal
        sig = MLSignal(entity_id="E1")
        assert sig.xgboost_probability is None
        assert sig.is_anomaly is None
        assert sig.feature_values is None
        assert sig.explanation is None
        assert sig.top_features is None

    def test_ml_signal_full_construction(self):
        from backend.app.analytics.models import MLSignal
        sig = MLSignal(
            entity_id="E1",
            xgboost_probability=0.8,
            is_anomaly=True,
            anomaly_score=-0.5,
            feature_values={"centrality_degree": 1.5},
            top_features=["centrality_degree"],
            explanation="High-risk. Requires investigator review. Synthetic development target.",
        )
        assert sig.entity_id == "E1"
        assert sig.is_anomaly is True
        assert sig.feature_values["centrality_degree"] == 1.5

    def test_ml_train_response_construction(self):
        from backend.app.analytics.models import MLTrainResponse
        resp = MLTrainResponse(
            status="success",
            xgboost_version="v1",
            isolation_forest_version="v1",
            metrics={"roc_auc": 0.75},
        )
        assert resp.status == "success"

    def test_ml_inference_response_construction(self):
        from backend.app.analytics.models import MLInferenceResponse, MLSignal
        resp = MLInferenceResponse(
            case_id="CASE-X",
            signals=[MLSignal(entity_id="E1", xgboost_probability=0.5)],
            metadata={"feature_schema_version": "1.0"},
        )
        assert resp.case_id == "CASE-X"
        assert len(resp.signals) == 1
