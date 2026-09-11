import pytest
from backend.app.extraction.providers.implementations.transformer_ner import TransformerEntityExtractor

def test_transformer_ner_wordpiece_merging():
    extractor = TransformerEntityExtractor()
    
    # Text that naturally forces BERT to create subwords: 'Aanya', 'Kulkarni'
    text = "Aanya Kulkarni is employed by Synthetic Organization 01798."
    
    spans = extractor.extract(text)
    
    # We should NOT see 'A', '##any', '##a', 'Kulkarni' as separate spans.
    # Instead, we should see 'Aanya Kulkarni' and 'Synthetic Organization'
    
    texts = [s.text for s in spans]
    
    assert "Aanya Kulkarni" in texts, f"Expected 'Aanya Kulkarni' to be merged, got: {texts}"
    assert "Synthetic Organization" in texts, f"Expected 'Synthetic Organization', got: {texts}"
    
    # Ensure there are no wordpieces
    for s in spans:
        assert "##" not in s.text, f"Subword fragments leaked into output: {s.text}"
        
    # Check start and end offsets
    aanya_span = next(s for s in spans if s.text == "Aanya Kulkarni")
    assert aanya_span.start_char == 0
    assert aanya_span.end_char == 14
    assert aanya_span.label == "PER"
    
    org_span = next(s for s in spans if s.text == "Synthetic Organization")
    assert org_span.start_char == 30
    assert org_span.end_char == 52
    assert org_span.label == "ORG"
