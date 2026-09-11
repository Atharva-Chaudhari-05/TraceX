import pytest
from backend.app.extraction.providers.implementations.transformer_re import TransformerRelationExtractor
from backend.app.extraction.providers.base import ExtractedSpan
from backend.app.extraction.pipeline import ExtractionPipeline

@pytest.fixture(scope="module")
def luke_extractor():
    """Load LUKE model once for the entire test module to save time."""
    extractor = TransformerRelationExtractor()
    return extractor

def test_luke_model_loading(luke_extractor):
    assert luke_extractor.model is not None
    assert luke_extractor.tokenizer is not None
    assert luke_extractor.model.__class__.__name__ == "LukeForEntityPairClassification"
    assert luke_extractor.tokenizer.__class__.__name__ == "LukeTokenizer"

def test_checkpoint_classification_head(luke_extractor):
    # Verify the classifier head has 42 classes for TACRED
    assert hasattr(luke_extractor.model, 'classifier')
    assert luke_extractor.model.config.num_labels == 42
    assert len(luke_extractor.model.config.id2label) == 42

def test_luke_per_employee_of(luke_extractor):
    # "John works for Google." -> John (0,4), Google (15,21)
    sentence = "John works for Google."
    subj_span = ExtractedSpan(text="John", label="PER", start_char=0, end_char=4, method="test", confidence=1.0, metadata={})
    obj_span = ExtractedSpan(text="Google", label="ORG", start_char=15, end_char=21, method="test", confidence=1.0, metadata={})
    
    rel_data = luke_extractor.extract_relations(sentence, subj_span, obj_span, 0, 15)
    
    assert rel_data is not None
    assert rel_data["tracex_relationship"] == "WORKS_FOR"
    assert rel_data["direction"] == "SUBJ_TO_OBJ"
    assert rel_data["tacred_label"] == "per:employee_of"
    assert rel_data["confidence"] > 0.90

def test_luke_no_relation(luke_extractor):
    # "John looked at the building of Google." -> John (0,4), Google (31,37)
    sentence = "John looked at the building of Google."
    subj_span = ExtractedSpan(text="John", label="PER", start_char=0, end_char=4, method="test", confidence=1.0, metadata={})
    obj_span = ExtractedSpan(text="Google", label="ORG", start_char=31, end_char=37, method="test", confidence=1.0, metadata={})
    
    rel_data = luke_extractor.extract_relations(sentence, subj_span, obj_span, 0, 31)
    
    # no_relation should return None
    assert rel_data is None

def test_luke_invalid_spans(luke_extractor):
    sentence = "John works for Google."
    subj_span = ExtractedSpan(text="John", label="PER", start_char=0, end_char=4, method="test", confidence=1.0, metadata={})
    obj_span = ExtractedSpan(text="Google", label="ORG", start_char=15, end_char=21, method="test", confidence=1.0, metadata={})
    
    # Overlapping spans (e.g. 0,4 and 2,8)
    rel_data_overlap = luke_extractor.extract_relations(sentence, subj_span, obj_span, 0, 2)
    assert rel_data_overlap is None
    
    # Out of bounds
    rel_data_oob = luke_extractor.extract_relations(sentence, subj_span, obj_span, 0, 100)
    assert rel_data_oob is None
    
    # Negative bounds
    rel_data_neg = luke_extractor.extract_relations(sentence, subj_span, obj_span, -1, 15)
    assert rel_data_neg is None

def test_graceful_luke_failure(luke_extractor):
    # Pass a valid sentence but force an exception in tokenizer or model
    # To test graceful failure
    sentence = "John works for Google."
    subj_span = ExtractedSpan(text="John", label="PER", start_char=0, end_char=4, method="test", confidence=1.0, metadata={})
    obj_span = ExtractedSpan(text="Google", label="ORG", start_char=15, end_char=21, method="test", confidence=1.0, metadata={})
    
    # Temporarily break tokenizer
    original_tokenizer = luke_extractor.tokenizer
    luke_extractor.tokenizer = None
    
    rel_data = luke_extractor.extract_relations(sentence, subj_span, obj_span, 0, 15)
    assert rel_data is None
    
    luke_extractor.tokenizer = original_tokenizer

def test_pipeline_regression_and_candidate_filtering():
    # Test regression of Regex + spaCy + BERT NER
    pipeline = ExtractionPipeline()
    # Mock the transformer RE to avoid running it for this specific fast test, or just let it run.
    # It will run fast enough.
    
    text = "Call John at 555-123-4567. He works for Google in New York."
    entities, relationships = pipeline.process(text)
    
    # Check entities (Regex, spaCy/BERT)
    phone = next((e for e in entities if e.label == "Phone" and e.text == "555-123-4567"), None)
    assert phone is not None
    
    john = next((e for e in entities if e.text == "John"), None)
    assert john is not None
    
    google = next((e for e in entities if e.text == "Google" and e.label == "ORG"), None)
    assert google is not None
    
    # Check Candidate Pair Filtering & Correct TraceX mapping
    # Since "He works for Google in New York" doesn't have "John" in the same sentence as "Google", 
    # it won't pair them if sentence bounded.
    # Let's change text so they are in the same sentence.
    text2 = "John works for Google."
    entities2, relationships2 = pipeline.process(text2)
    
    john2 = next((e for e in entities2 if e.text == "John"), None)
    google2 = next((e for e in entities2 if e.text == "Google" and e.label == "ORG"), None)
    
    assert john2 is not None and google2 is not None
    
    # LUKE should have found the relation
    rel = next((r for r in relationships2 if r["source_span"].text == "John" and r["target_span"].text == "Google"), None)
    assert rel is not None
    assert rel["tracex_relationship"] == "WORKS_FOR"
    assert rel["direction"] == "SUBJ_TO_OBJ"
