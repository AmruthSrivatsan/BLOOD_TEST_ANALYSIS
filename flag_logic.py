"""Helpers for deterministic lab test flag computation."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional

RANGE_PATTERN = re.compile(
    r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|–|—|to|TO|\u2013|\u2014)\s*(?P<high>-?\d+(?:\.\d+)?)"
)
SINGLE_BOUND_PATTERN = re.compile(
    r"(?P<symbol><=|>=|<|>)\s*(?P<value>-?\d+(?:\.\d+)?)"
)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")


@dataclass
class ParsedRange:
    low: Optional[float] = None
    high: Optional[float] = None

    def classify(self, value: float) -> str:
        if self.low is None or self.high is None:
            return ""
        if value < self.low:
            return "low"
        if value > self.high:
            return "high"
        return "normal"


def _parse_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_range(reference_range: str) -> ParsedRange:
    if not reference_range:
        return ParsedRange()

    ref = reference_range.replace("to", "-").replace("TO", "-")
    ref = ref.replace("–", "-").replace("—", "-").strip()

    match = RANGE_PATTERN.search(ref)
    if match:
        low = _parse_float(match.group("low"))
        high = _parse_float(match.group("high"))
        if low is not None and high is not None:
            if low > high:
                low, high = high, low
            return ParsedRange(low=low, high=high)

    match = SINGLE_BOUND_PATTERN.search(ref)
    if match:
        value = _parse_float(match.group("value"))
        if value is None:
            return ParsedRange()
        symbol = match.group("symbol")
        if symbol in {">", ">="}:
            return ParsedRange(low=value, high=None)
        if symbol in {"<", "<="}:
            return ParsedRange(low=None, high=value)

    numbers = [
        _parse_float(num)
        for num in NUMBER_PATTERN.findall(ref)
    ]
    if len(numbers) >= 2 and numbers[0] is not None and numbers[1] is not None:
        low = min(numbers[0], numbers[1])
        high = max(numbers[0], numbers[1])
        return ParsedRange(low=low, high=high)

    return ParsedRange()


def compute_flag(value: str, reference_range: str) -> str:
    """Return a deterministic flag based on numeric comparison."""
    numeric_value = _parse_float(str(value).strip())
    if numeric_value is None:
        return ""

    parsed_range = _parse_range(reference_range)
    if parsed_range.low is None or parsed_range.high is None:
        return ""

    return parsed_range.classify(numeric_value)
