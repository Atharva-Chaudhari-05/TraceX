import logging
from typing import List

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

from backend.app.extraction.providers.base import EntityExtractorProtocol, ExtractedSpan

logger = logging.getLogger(__name__)

class TransformerEntityExtractor(EntityExtractorProtocol):
    """
    Named Entity Recognition using a pre-trained transformer model (dslim/bert-base-NER).
    Extracts PER, ORG, LOC, and MISC.
    Ignores MISC as per TraceX rules.
    """
    
    def __init__(self, model_id: str = "dslim/bert-base-NER"):
        self.model_id = model_id
        self._nlp = None
        self._load_model()
        
    def _load_model(self):
        try:
            logger.info(f"Loading Transformer NER model: {self.model_id}")
            # Load tokenizer and model
            # Note: We must use aggregation_strategy="simple" to group subwords into full words/entities
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_id)
            self._nlp = pipeline(
                "ner", 
                model=self.model, 
                tokenizer=self.tokenizer, 
                aggregation_strategy="simple",
                device=-1  # Force CPU for M4 requirements
            )
            logger.info("Transformer NER model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Transformer NER model {self.model_id}: {e}")
            raise
            
    def extract(self, text: str) -> List[ExtractedSpan]:
        if not text.strip():
            return []
            
        if not self._nlp:
            logger.warning("Transformer NER model not loaded. Skipping extraction.")
            return []
            
        spans = []
        try:
            # The pipeline returns a list of dicts: {'entity_group': 'PER', 'score': 0.99, 'word': 'John', 'start': 0, 'end': 4}
            results = self._nlp(text)
            
            merged_results = []
            for res in results:
                entity_group = res.get('entity_group', '')
                if entity_group == 'MISC' or not entity_group:
                    continue
                
                # Merge contiguous subwords (e.g. 'A', '##any', '##a') if they share the same label
                # 'simple' aggregation strategy in transformers usually merges them, but if they
                # are separated by space or the tokenizer yields disjoint B-PER I-PER spans, we merge them
                # if they are within 1 character distance of each other.
                if merged_results:
                    prev = merged_results[-1]
                    if prev['entity_group'] == entity_group and (res['start'] - prev['end'] <= 1):
                        prev['end'] = res['end']
                        # Average the confidence
                        prev['score'] = float((prev['score'] + float(res.get('score', 0.0))) / 2.0)
                        continue
                        
                merged_results.append({
                    'entity_group': entity_group,
                    'start': res.get('start', 0),
                    'end': res.get('end', 0),
                    'score': float(res.get('score', 0.0)),
                })
            
            for m in merged_results:
                spans.append(
                    ExtractedSpan(
                        text=text[m['start']:m['end']],
                        label=m['entity_group'],
                        start_char=m['start'],
                        end_char=m['end'],
                        confidence=m['score'],
                        method="transformer_ner",
                        metadata={"model": self.model_id}
                    )
                )
        except Exception as e:
            logger.error(f"Transformer NER extraction failed: {e}")
            # Let the caller handle the failure according to the M4 degraded mode plan
            raise
            
        return spans
