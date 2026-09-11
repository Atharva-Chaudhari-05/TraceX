from typing import List

import spacy

from backend.app.extraction.providers.base import EntityExtractorProtocol, ExtractedSpan


class SpacyEntityExtractor(EntityExtractorProtocol):
    def __init__(self, model_name: str = "en_core_web_sm"):
        # Load the spacy model
        self.nlp = spacy.load(model_name)
        
        # Map spaCy entity labels to canonical graph labels
        self.label_mapping = {
            "PERSON": "Person",
            "ORG": "Organization",
            "GPE": "Location",
            "LOC": "Location",
            "FAC": "Location",
            "MONEY": "Transaction", # Though mostly we want distinct entity resolution
            "DATE": "Event",
            "TIME": "Event"
        }

    def extract(self, text: str) -> List[ExtractedSpan]:
        doc = self.nlp(text)
        spans = []
        
        for ent in doc.ents:
            canonical_label = self.label_mapping.get(ent.label_)
            if canonical_label:
                spans.append(
                    ExtractedSpan(
                        text=ent.text,
                        label=canonical_label,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=0.85, # Base MVP confidence for spaCy
                        method="spacy_ner",
                        metadata={"spacy_label": ent.label_}
                    )
                )
                
        return spans
