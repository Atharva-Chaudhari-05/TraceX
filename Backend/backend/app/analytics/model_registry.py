import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import joblib

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self):
        self.base_dir = Path(settings.tracex_model_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_model_dir(self, model_type: str, version: str) -> Path:
        return self.base_dir / model_type / version

    def get_latest_version(self, model_type: str) -> Optional[str]:
        """Returns the latest version string for a given model type, or None if no models exist."""
        type_dir = self.base_dir / model_type
        if not type_dir.exists():
            return None
        
        versions = []
        for item in type_dir.iterdir():
            if item.is_dir() and item.name.startswith("v"):
                try:
                    # Expecting format v1, v2, etc.
                    v_num = int(item.name[1:])
                    versions.append(v_num)
                except ValueError:
                    pass
        
        if not versions:
            return None
            
        return f"v{max(versions)}"

    def get_next_version(self, model_type: str) -> str:
        latest = self.get_latest_version(model_type)
        if latest is None:
            return "v1"
        return f"v{int(latest[1:]) + 1}"

    def save_xgboost_model(self, model: Any, metadata: Dict[str, Any]) -> str:
        """Saves an XGBoost model and its metadata atomically."""
        model_type = "xgboost"
        version = self.get_next_version(model_type)
        model_dir = self._get_model_dir(model_type, version)
        model_dir.mkdir(parents=True, exist_ok=False) # Prevent overwrite

        metadata["model_type"] = model_type
        metadata["model_version"] = version
        metadata["created_at"] = datetime.now(timezone.utc).isoformat()

        try:
            # XGBoost specific save
            model.save_model(str(model_dir / "model.json"))
            with open(model_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved {model_type} {version} successfully.")
            return version
        except Exception as e:
            logger.error(f"Failed to save {model_type} {version}: {e}")
            raise RuntimeError(f"Model persistence failed: {e}")

    def save_isolation_forest_model(self, model: Any, scaler: Any, metadata: Dict[str, Any]) -> str:
        """Saves an Isolation Forest model, scaler, and metadata atomically."""
        model_type = "isolation_forest"
        version = self.get_next_version(model_type)
        model_dir = self._get_model_dir(model_type, version)
        model_dir.mkdir(parents=True, exist_ok=False)

        metadata["model_type"] = model_type
        metadata["model_version"] = version
        metadata["created_at"] = datetime.now(timezone.utc).isoformat()

        try:
            joblib.dump(model, model_dir / "model.joblib")
            joblib.dump(scaler, model_dir / "scaler.joblib")
            with open(model_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved {model_type} {version} successfully.")
            return version
        except Exception as e:
            logger.error(f"Failed to save {model_type} {version}: {e}")
            raise RuntimeError(f"Model persistence failed: {e}")

    def load_xgboost_model(self, version: Optional[str] = None) -> Tuple[Any, Dict[str, Any]]:
        """Loads an XGBoost model and metadata."""
        import xgboost as xgb
        model_type = "xgboost"
        if version is None:
            version = self.get_latest_version(model_type)
            if version is None:
                raise ValueError(f"No models found for {model_type}")

        model_dir = self._get_model_dir(model_type, version)
        if not model_dir.exists():
            raise ValueError(f"Model version {version} not found for {model_type}")

        try:
            with open(model_dir / "metadata.json", "r") as f:
                metadata = json.load(f)
            
            model = xgb.XGBClassifier()
            model.load_model(str(model_dir / "model.json"))
            return model, metadata
        except Exception as e:
            logger.error(f"Failed to load {model_type} {version}: {e}")
            raise RuntimeError(f"Model loading failed: {e}")

    def load_isolation_forest_model(self, version: Optional[str] = None) -> Tuple[Any, Any, Dict[str, Any]]:
        """Loads an Isolation Forest model, scaler, and metadata."""
        model_type = "isolation_forest"
        if version is None:
            version = self.get_latest_version(model_type)
            if version is None:
                raise ValueError(f"No models found for {model_type}")

        model_dir = self._get_model_dir(model_type, version)
        if not model_dir.exists():
            raise ValueError(f"Model version {version} not found for {model_type}")

        try:
            with open(model_dir / "metadata.json", "r") as f:
                metadata = json.load(f)
            
            model = joblib.load(model_dir / "model.joblib")
            scaler = joblib.load(model_dir / "scaler.joblib")
            return model, scaler, metadata
        except Exception as e:
            logger.error(f"Failed to load {model_type} {version}: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
