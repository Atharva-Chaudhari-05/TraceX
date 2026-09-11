from typing import Protocol, List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedSpan:
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float
    method: str
    metadata: Dict[str, Any]


class LanguageDetectorProtocol(Protocol):
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect the primary language of the text. Returns (lang_code, confidence)."""
        ...


class RegexExtractorProtocol(Protocol):
    def extract(self, text: str) -> List[ExtractedSpan]:
        """Extract high-confidence patterns using regular expressions."""
        ...


class EntityExtractorProtocol(Protocol):
    def extract(self, text: str) -> List[ExtractedSpan]:
        """Extract named entities from text."""
        ...
