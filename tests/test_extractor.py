"""Minimal smoke test for the extraction pipeline."""
from __future__ import annotations

import json

from extractor import ReportExtractor

SAMPLE_TEXT = """
Patient Name: Jane Doe  Age: 45  Gender: Female
Hemoglobin 11.2 g/dL 12 - 16
Platelet Count 420 x10^3/uL 150-400
""".strip()


def run_sample() -> None:
    extractor = ReportExtractor()
    result = extractor.extract_from_text(SAMPLE_TEXT, source_filename="sample.txt")
    print(json.dumps(result, indent=2))
    assert result["tests"], "Expected at least one parsed test"


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    run_sample()
