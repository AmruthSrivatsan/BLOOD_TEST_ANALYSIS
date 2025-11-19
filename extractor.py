"""Robust extraction utilities for lab reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import io
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Tuple

import fitz  # PyMuPDF
from PIL import Image

try:  # Optional OCR for image uploads
    import pytesseract
except Exception:  # pragma: no cover - pytesseract is optional at runtime
    pytesseract = None

from flag_logic import compute_flag

VALUE_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
RANGE_PATTERN = re.compile(
    r"-?\d+(?:\.\d+)?\s*(?:-|–|—|to|TO|\u2013|\u2014)\s*-?\d+(?:\.\d+)?"
)

PATIENT_FIELD_PATTERNS = {
    "name": [r"Patient Name\s*[:\-]\s*(.+)", r"Name\s*[:\-]\s*(.+)"],
    "age": [r"Age\s*[:\-]\s*(.+)"],
    "gender": [r"Gender\s*[:\-]\s*(.+)", r"Sex\s*[:\-]\s*(.+)"],
    "patient_id": [r"Patient ID\s*[:\-]\s*(.+)", r"ID\s*[:\-]\s*(.+)"],
    "date_of_report": [r"Date\s*[:\-]\s*(.+)", r"Date of Report\s*[:\-]\s*(.+)"],
    "referring_doctor": [r"Ref(?:erring)? Doctor\s*[:\-]\s*(.+)"],
    "laboratory_name": [r"Laboratory\s*[:\-]\s*(.+)", r"Lab Name\s*[:\-]\s*(.+)"],
}


def _clean_text(value: str) -> str:
    return value.strip().strip("-:")


def _extract_patient_details(text: str) -> Dict[str, str]:
    details = {key: "" for key in PATIENT_FIELD_PATTERNS}
    for key, patterns in PATIENT_FIELD_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details[key] = _clean_text(match.group(1))
                break
    return details


def _iter_clean_lines(text: str) -> Iterable[str]:
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue
        yield line


def _parse_test_line(line: str) -> Dict[str, str] | None:
    lowered = line.lower()
    if any(keyword in lowered for keyword in (
        "patient", "referring", "doctor", "lab", "report", "age", "gender"
    )):
        return None

    if sum(char.isdigit() for char in line) == 0:
        return None

    value_match = VALUE_PATTERN.search(line)
    if not value_match:
        return None

    name = line[: value_match.start()].strip("-: ")
    if len(name) < 2:
        return None

    remainder = line[value_match.end() :].strip()
    ref_match = RANGE_PATTERN.search(remainder)
    reference_range = ref_match.group().strip() if ref_match else ""
    unit = remainder[: ref_match.start()].strip("-: ") if ref_match else remainder.strip()

    return {
        "name": name,
        "value": value_match.group().strip(),
        "unit": unit,
        "reference_range": reference_range,
        "flag": "",
        "raw_text_snippet": line.strip(),
    }


def _parse_tests(text: str) -> List[Dict[str, str]]:
    tests: List[Dict[str, str]] = []
    for line in _iter_clean_lines(text):
        parsed = _parse_test_line(line)
        if parsed:
            tests.append(parsed)
    return tests


def _sanitize_tests(tests: List[Dict[str, str]]) -> List[Dict[str, str]]:
    sanitized: List[Dict[str, str]] = []
    for test in tests:
        normalized = {
            "name": str(test.get("name", "")).strip(),
            "value": str(test.get("value", "")).strip(),
            "unit": str(test.get("unit", "")).strip(),
            "reference_range": str(test.get("reference_range", "")).strip(),
            "flag": str(test.get("flag", "")).strip(),
            "raw_text_snippet": str(test.get("raw_text_snippet", "")).strip(),
        }
        if not normalized["flag"]:
            normalized["flag"] = compute_flag(
                normalized["value"], normalized["reference_range"]
            )
        sanitized.append(normalized)
    return sanitized


@dataclass
class ExtractionResult:
    patient_details: Dict[str, str] = field(default_factory=dict)
    report_metadata: Dict[str, Any] = field(default_factory=dict)
    tests: List[Dict[str, str]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "patient_details": self.patient_details,
            "report_metadata": self.report_metadata,
            "tests": self.tests,
        }


class ReportExtractor:
    """High-level orchestration for deterministic report extraction."""

    def __init__(self):
        pass

    def extract(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            text, num_pages = self._extract_pdf_text(file_bytes)
        else:
            text = self._extract_image_text(file_bytes)
            num_pages = 1
        return self.extract_from_text(text, filename, num_pages)

    def extract_from_text(
        self, text: str, source_filename: str, num_pages: int = 1
    ) -> Dict[str, Any]:
        patient_details = _extract_patient_details(text)
        tests = _sanitize_tests(_parse_tests(text))
        metadata = {
            "source_filename": source_filename,
            "num_pages": num_pages,
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        result = ExtractionResult(
            patient_details=patient_details,
            report_metadata=metadata,
            tests=tests,
        )
        return result.as_dict()

    def _extract_pdf_text(self, file_bytes: bytes) -> Tuple[str, int]:
        document = fitz.open(stream=file_bytes, filetype="pdf")
        texts: List[str] = []
        for page in document:
            texts.append(page.get_text("text"))
        combined = "\n".join(texts)
        return combined, len(document)

    def _extract_image_text(self, file_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(file_bytes))
        if pytesseract is None:
            raise RuntimeError(
                "pytesseract is not available. Install it to enable image extraction."
            )
        return pytesseract.image_to_string(image)
