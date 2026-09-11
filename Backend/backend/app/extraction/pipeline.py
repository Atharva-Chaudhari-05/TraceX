from typing import List, Optional, Tuple, Dict
import logging

from backend.app.extraction.providers.base import (
    LanguageDetectorProtocol,
    RegexExtractorProtocol,
    EntityExtractorProtocol,
    ExtractedSpan
)
from backend.app.extraction.providers.implementations.language_detector import SpacyLanguageDetector
from backend.app.extraction.providers.implementations.regex_extractor import StandardRegexExtractor
from backend.app.extraction.providers.implementations.spacy_extractor import SpacyEntityExtractor

# Import the new transformer extractors
from backend.app.extraction.providers.implementations.transformer_ner import TransformerEntityExtractor
from backend.app.extraction.providers.implementations.transformer_re import TransformerRelationExtractor

logger = logging.getLogger(__name__)

class ExtractionPipeline:
    def __init__(
        self,
        language_detector: Optional[LanguageDetectorProtocol] = None,
        regex_extractor: Optional[RegexExtractorProtocol] = None,
        entity_extractor: Optional[EntityExtractorProtocol] = None,
        transformer_ner: Optional[EntityExtractorProtocol] = None,
        transformer_re: Optional[TransformerRelationExtractor] = None
    ):
        self.language_detector = language_detector or SpacyLanguageDetector()
        self.regex_extractor = regex_extractor or StandardRegexExtractor()
        self.entity_extractor = entity_extractor or SpacyEntityExtractor()
        
        # Transformer-based models
        self.transformer_ner = transformer_ner or TransformerEntityExtractor()
        self.transformer_re = transformer_re or TransformerRelationExtractor()
        
        self.supported_languages = {"en"}

    def _split_into_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Use spaCy to split text into sentences, returning (sentence_text, start_char, end_char).
        """
        if hasattr(self.entity_extractor, "nlp") and self.entity_extractor.nlp:
            doc = self.entity_extractor.nlp(text)
            return [(sent.text, sent.start_char, sent.end_char) for sent in doc.sents]
        return [(text, 0, len(text))]

    def process(self, text: str) -> Tuple[List[ExtractedSpan], List[Dict]]:
        """
        Processes text sequentially and returns (entities, relationships).
        """
        if not text or not text.strip():
            return [], []

        # 1. Language Detection
        lang, lang_confidence = self.language_detector.detect_language(text)
        if lang not in self.supported_languages:
            logger.warning(f"Unsupported language detected: {lang} (confidence: {lang_confidence})")
            return [], []

        all_spans = []

        # 2. Regex Extraction
        try:
            regex_spans = self.regex_extractor.extract(text)
            all_spans.extend(regex_spans)
        except Exception as e:
            logger.error(f"Regex extraction failed: {e}")

        # 3. spaCy Extraction
        try:
            nlp_spans = self.entity_extractor.extract(text)
            all_spans.extend(nlp_spans)
        except Exception as e:
            logger.error(f"NLP entity extraction failed: {e}")

        # 4. Transformer NER Extraction
        try:
            transformer_spans = self.transformer_ner.extract(text)
            all_spans.extend(transformer_spans)
        except Exception as e:
            logger.error(f"Transformer NER extraction failed: {e}")
            # Degrade gracefully, do not fail

        # Deduplicate spans based on exact character boundaries to avoid redundant RE pairs
        unique_spans_map = {}
        for span in all_spans:
            key = (span.start_char, span.end_char, span.label)
            if key not in unique_spans_map or unique_spans_map[key].confidence < span.confidence:
                unique_spans_map[key] = span
                
        deduped_spans = list(unique_spans_map.values())
        
        # 5. Candidate Pair Filtering & 6. Relation Extraction
        relationships = []
        try:
            sentences = self._split_into_sentences(text)
            for sent_text, sent_start, sent_end in sentences:
                # Find all entities in this sentence
                sent_entities = [s for s in deduped_spans if s.start_char >= sent_start and s.end_char <= sent_end]
                
                # Pair generation
                for i, subj in enumerate(sent_entities):
                    for obj in sent_entities[i+1:]:
                        if subj == obj: continue
                        
                        # Basic type filtering based on TACRED mapping (PER+ORG, PER+LOC, PER+PER, ORG+LOC)
                        valid_pairs = [
                            ("PER", "ORG"), ("ORG", "PER"),
                            ("PER", "LOC"), ("LOC", "PER"),
                            ("PER", "PER"),
                            ("ORG", "LOC"), ("LOC", "ORG")
                        ]
                        # Assume MISC is ignored, labels are standard
                        subj_base = subj.label.replace("B-", "").replace("I-", "")
                        obj_base = obj.label.replace("B-", "").replace("I-", "")
                        
                        if (subj_base, obj_base) not in valid_pairs:
                            continue
                            
                        subj_offset_in_sent = subj.start_char - sent_start
                        obj_offset_in_sent = obj.start_char - sent_start
                        
                        rel_data = self.transformer_re.extract_relations(
                            sent_text, subj, obj, subj_offset_in_sent, obj_offset_in_sent
                        )
                        if rel_data:
                            # Add to relationships
                            relationships.append({
                                "source_span": subj,
                                "target_span": obj,
                                "tracex_relationship": rel_data["tracex_relationship"],
                                "direction": rel_data["direction"],
                                "confidence": rel_data["confidence"],
                                "tacred_label": rel_data["tacred_label"],
                                "evidence_span": sent_text,
                                "extraction_method": "transformer_re"
                            })
                            
        except Exception as e:
            logger.error(f"Transformer Relation Extraction failed: {e}")
            # Degrade gracefully

        return deduped_spans, relationships
