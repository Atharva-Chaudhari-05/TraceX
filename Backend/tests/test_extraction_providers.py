import pytest
from backend.app.extraction.providers.implementations.regex_extractor import StandardRegexExtractor
from backend.app.extraction.providers.implementations.spacy_extractor import SpacyEntityExtractor
from backend.app.extraction.providers.implementations.language_detector import SpacyLanguageDetector


def test_regex_extractor():
    extractor = StandardRegexExtractor()
    text = "Call me at 555-123-4567 or email john.doe@example.com."
    
    spans = extractor.extract(text)
    
    # Expecting 1 Phone and 1 Email
    assert len(spans) == 2
    
    phone_span = next((s for s in spans if s.label == "Phone"), None)
    email_span = next((s for s in spans if s.label == "Email"), None)
    
    assert phone_span is not None
    assert phone_span.text == "555-123-4567"
    assert phone_span.method == "regex"
    assert phone_span.confidence == 0.95
    
    assert email_span is not None
    assert email_span.text == "john.doe@example.com"
    assert email_span.method == "regex"


def test_spacy_extractor():
    extractor = SpacyEntityExtractor(model_name="en_core_web_sm")
    text = "John Doe works at Google in New York."
    
    spans = extractor.extract(text)
    
    # Should find John Doe (Person), Google (Organization), New York (Location)
    assert len(spans) >= 3
    
    person_span = next((s for s in spans if s.label == "Person" and "John Doe" in s.text), None)
    org_span = next((s for s in spans if s.label == "Organization" and "Google" in s.text), None)
    loc_span = next((s for s in spans if s.label == "Location" and "New York" in s.text), None)
    
    assert person_span is not None
    assert person_span.method == "spacy_ner"
    assert person_span.confidence == 0.85
    
    assert org_span is not None
    assert loc_span is not None


def test_language_detector():
    detector = SpacyLanguageDetector(model_name="en_core_web_sm")
    lang, conf = detector.detect_language("Some random text")
    
    assert lang == "en"
    assert conf > 0.9
