import re
from typing import List

from backend.app.extraction.providers.base import RegexExtractorProtocol, ExtractedSpan


class StandardRegexExtractor(RegexExtractorProtocol):
    def __init__(self):
        # Basic patterns for MVP.
        # Can be expanded based on the domain requirements.
        self.patterns = {
            "Phone": re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b'),
            "Account": re.compile(r'\b[A-Z]{2}[0-9]{2}(?:[ ]?[0-9a-zA-Z]{4}){4}(?:[ ]?[0-9a-zA-Z]{1,2})?\b'), # IBAN
            "Email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
            "Device": re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b') # IP Address
        }

    def extract(self, text: str) -> List[ExtractedSpan]:
        spans = []
        for label, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                # Ensure the confidence is distinct from M5 Match_Score
                # Regex matches are highly confident if the pattern matches.
                spans.append(
                    ExtractedSpan(
                        text=match.group().strip(),
                        label=label,
                        start_char=match.start(),
                        end_char=match.end(),
                        confidence=0.95,
                        method="regex",
                        metadata={}
                    )
                )
        return spans
