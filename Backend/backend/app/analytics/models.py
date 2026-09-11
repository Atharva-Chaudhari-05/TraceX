from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class InsightType(str, Enum):
    HIGH_ACTIVITY = "HIGH_ACTIVITY"
    HIGH_INFLUENCE = "HIGH_INFLUENCE"
    CRITICAL_BRIDGE = "CRITICAL_BRIDGE"
    COMMUNITY_DETECTED = "COMMUNITY_DETECTED"

class Explanation(BaseModel):
    what: str
    why: str
    supporting_evidence: List[str] = Field(default_factory=list)
    provenance: str

class KeyEntity(BaseModel):
    entity_id: str
    metric: str
    score: float
    explanation: Explanation

class Community(BaseModel):
    community_id: int
    size: int
    central_entity_id: str
    member_ids: List[str]
    explanation: Explanation

class NetworkAnalyticsResponse(BaseModel):
    case_id: str
    node_count: int
    edge_count: int
    key_entities: List[KeyEntity] = Field(default_factory=list)
    communities: List[Community] = Field(default_factory=list)

class MLTrainRequest(BaseModel):
    case_ids: List[str]
    target_definition: str = "synthetic_dev_target_v1"

class MLTrainResponse(BaseModel):
    status: str
    xgboost_version: str
    isolation_forest_version: str
    metrics: Dict[str, Any]

class MLSignal(BaseModel):
    entity_id: str
    xgboost_probability: Optional[float] = None
    is_anomaly: Optional[bool] = None
    anomaly_score: Optional[float] = None
    # Explainability fields (CHECK 8)
    feature_values: Optional[Dict[str, float]] = None
    top_features: Optional[List[str]] = None
    explanation: Optional[str] = None

class MLInferenceResponse(BaseModel):
    case_id: str
    signals: List[MLSignal]
    metadata: Dict[str, Any]
