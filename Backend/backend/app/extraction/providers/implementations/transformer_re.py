import logging
from typing import Optional
import torch
from transformers import LukeTokenizer, LukeForEntityPairClassification

from backend.app.extraction.providers.base import ExtractedSpan

logger = logging.getLogger(__name__)

# TACRED to TraceX Relationship Map
# As explicitly defined in the approved M4 Implementation Plan
TACRED_TO_TRACEX = {
    "per:employee_of": ("WORKS_FOR", "SUBJ_TO_OBJ"),
    "org:top_members/employees": ("WORKS_FOR", "OBJ_TO_SUBJ"),
    "per:cities_of_residence": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "per:stateorprovinces_of_residence": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "per:countries_of_residence": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "org:city_of_headquarters": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "org:stateorprovince_of_headquarters": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "org:country_of_headquarters": ("LOCATED_AT", "SUBJ_TO_OBJ"),
    "per:spouse": ("ASSOCIATED_WITH", "BIDIRECTIONAL"),
    "per:siblings": ("ASSOCIATED_WITH", "BIDIRECTIONAL"),
    "per:other_family": ("ASSOCIATED_WITH", "BIDIRECTIONAL"),
    "per:parents": ("ASSOCIATED_WITH", "BIDIRECTIONAL"),
    "per:children": ("ASSOCIATED_WITH", "BIDIRECTIONAL"),
}

class TransformerRelationExtractor:
    """
    Relation Extraction using a pre-trained LUKE model (studio-ousia/luke-large-finetuned-tacred).
    Extracts TACRED relations via entity pair classification and maps them to TraceX vocabulary.
    """
    
    def __init__(self, model_id: str = "studio-ousia/luke-large-finetuned-tacred"):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None
        self._load_model()
        
    def _load_model(self):
        try:
            logger.info(f"Loading LUKE RE model: {self.model_id}")
            self.tokenizer = LukeTokenizer.from_pretrained(self.model_id)
            self.model = LukeForEntityPairClassification.from_pretrained(self.model_id)
            self.model.eval()
            logger.info("LUKE RE model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load LUKE RE model {self.model_id}: {e}")
            # Degrade gracefully, don't crash startup

    def extract_relations(self, sentence: str, subj_span: ExtractedSpan, obj_span: ExtractedSpan, 
                          subj_offset_in_sentence: int, obj_offset_in_sentence: int) -> Optional[dict]:
        """
        Extract relation between a subject and object within a given sentence using exact character spans.
        Returns a dict with mapping details if a valid mapped relation is found.
        """
        if not self.model or not self.tokenizer:
            logger.warning("LUKE RE model not loaded. Skipping.")
            return None

        # Check bounds and spans logic
        if subj_offset_in_sentence < 0 or obj_offset_in_sentence < 0:
            return None
            
        subj_end = subj_offset_in_sentence + len(subj_span.text)
        obj_end = obj_offset_in_sentence + len(obj_span.text)
        
        # Check text bounds
        if subj_end > len(sentence) or obj_end > len(sentence):
            return None
            
        # Check overlapping spans
        if max(subj_offset_in_sentence, obj_offset_in_sentence) < min(subj_end, obj_end):
            return None

        try:
            entity_spans = [(subj_offset_in_sentence, subj_end), (obj_offset_in_sentence, obj_end)]
            inputs = self.tokenizer(sentence, entity_spans=entity_spans, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                pred_idx = torch.argmax(probs, dim=-1).item()
                confidence = probs[0][pred_idx].item()
                
            predicted_label = self.model.config.id2label[pred_idx]

            if predicted_label == "no_relation":
                return None

            if predicted_label in TACRED_TO_TRACEX:
                tracex_rel, direction = TACRED_TO_TRACEX[predicted_label]
                return {
                    "tracex_relationship": tracex_rel,
                    "direction": direction,
                    "confidence": confidence,
                    "tacred_label": predicted_label
                }
            return None
            
        except Exception as e:
            logger.error(f"LUKE RE extraction failed for pair: {e}")
            return None
