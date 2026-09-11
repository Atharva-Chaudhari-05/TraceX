import logging
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

class TargetProvider:
    def get_target_name(self) -> str:
        raise NotImplementedError

    def get_target_version(self) -> str:
        raise NotImplementedError

    def compute_targets(self, nodes: List[Dict]) -> pd.Series:
        """
        Computes the target values for the given nodes.
        Returns a pandas Series with the entity_id as the index.
        """
        raise NotImplementedError


class SyntheticDevTargetV1(TargetProvider):
    def __init__(self):
        # Deterministic, versioned development configuration
        self.known_synthetic_scenarios = {
            "SCN-FIN",
            "SCN-COM",
            "SCN-CYBER",
            "SCN-PHYS",
            "SCN-MIXED"
        }

    def get_target_name(self) -> str:
        return "synthetic_dev_target"

    def get_target_version(self) -> str:
        return "1.0"

    def compute_targets(self, nodes: List[Dict]) -> pd.Series:
        """
        A node receives target 1 if its canonical Neo4j Generation_Batch_ID
        belongs to the defined internal list of known synthetic crime-ring scenarios.
        Otherwise target 0.
        """
        target_dict = {}
        for n in nodes:
            node_id = n["id"]
            props = n.get("properties", {})
            batch_id = props.get("Generation_Batch_ID")
            
            if batch_id and any(batch_id.startswith(prefix) for prefix in self.known_synthetic_scenarios):
                target_dict[node_id] = 1
            else:
                target_dict[node_id] = 0

        series = pd.Series(target_dict, name="target")
        series.index.name = "entity_id"
        return series


def get_target_provider(definition: str) -> TargetProvider:
    """
    Factory to retrieve the appropriate TargetProvider based on definition.
    Unknown target definitions must raise a controlled error.
    """
    if definition == "synthetic_dev_target_v1":
        return SyntheticDevTargetV1()
    
    raise ValueError(f"Unknown target definition: {definition}")
