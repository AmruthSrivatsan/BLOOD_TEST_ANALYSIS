"""Task templates that operate on the canonical lab JSON."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TaskTemplate:
    key: str
    agent: str
    instructions: str


def build_task_templates() -> List[TaskTemplate]:
    base_intro = (
        "You receive a JSON object named structured_json."
        " It contains patient_details, report_metadata, and tests."
        " Each test includes name, value, unit, reference_range, and flag."
        " Do not fabricate metrics that are not present."
    )

    return [
        TaskTemplate(
            key="key_findings",
            agent="analyst",
            instructions=(
                f"{base_intro}\n\n"
                "Produce a concise bullet list (max 6 bullets) summarizing the"
                " most clinically relevant patterns. Mention exact values and"
                " whether they are high/low/normal using the flag field."
                " Respond in Markdown. JSON input:\n{{structured_json}}"
            ),
        ),
        TaskTemplate(
            key="health_concerns",
            agent="analyst",
            instructions=(
                f"{base_intro}\n\n"
                "List the main health concerns triggered by abnormal flags."
                " Explain why each abnormality matters in 2 sentences."
                " If everything is normal, explain that explicitly."
                " Respond in Markdown. JSON input:\n{{structured_json}}"
            ),
        ),
        TaskTemplate(
            key="recommended_tests",
            agent="researcher",
            instructions=(
                f"{base_intro}\n\n"
                "Suggest follow-up laboratory or imaging tests grounded in the"
                " data. Limit to 3-4 items. For each, describe the rationale"
                " referencing the specific lab values or flags."
                " Respond in Markdown. JSON input:\n{{structured_json}}"
            ),
        ),
        TaskTemplate(
            key="lifestyle_advice",
            agent="advisor",
            instructions=(
                f"{base_intro}\n\n"
                "Provide actionable lifestyle and self-care advice that aligns"
                " with the flagged lab values. Include diet, activity, and"
                " monitoring suggestions. Respond in Markdown. JSON input:\n{{structured_json}}"
            ),
        ),
        TaskTemplate(
            key="trusted_resources",
            agent="researcher",
            instructions=(
                f"{base_intro}\n\n"
                "Use the knowledge base tool to cite 2-3 reputable resources"
                " (e.g., CDC, WHO, specialty societies) that help the patient"
                " understand the findings. Each bullet should include a short"
                " justification. Respond in Markdown. JSON input:\n{{structured_json}}"
            ),
        ),
    ]
