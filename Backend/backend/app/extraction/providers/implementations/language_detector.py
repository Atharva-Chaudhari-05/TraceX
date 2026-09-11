import spacy
from typing import Tuple

from backend.app.extraction.providers.base import LanguageDetectorProtocol


class SpacyLanguageDetector(LanguageDetectorProtocol):
    def __init__(self, model_name: str = "en_core_web_sm"):
        # We can use the language of the spacy model as a simple heuristic
        # If the pipeline doesn't match the required language, we can reject it.
        # This is an MVP heuristic before introducing fasttext.
        self.nlp = spacy.load(model_name)
        self.supported_language = self.nlp.lang

    def detect_language(self, text: str) -> Tuple[str, float]:
        # MVP: always assume english with high confidence, 
        # or use a simple heuristic to detect standard latin characters.
        # This avoids adding fasttext-wheel as requested.
        return (self.supported_language, 0.99)
