"""Medical crew orchestration built on top of the structured JSON."""
from __future__ import annotations

import json
from typing import Any, Dict

from agents import build_agents
from tasks import build_task_templates


class MedicalCrew:
    """Runs the JSON-aware agents sequentially and returns sectioned outputs."""

    def __init__(self):
        self.agents = build_agents()
        self.task_templates = build_task_templates()

    def run(self, structured_json: Dict[str, Any]) -> Dict[str, str]:
        payload = json.dumps(structured_json, ensure_ascii=False, indent=2)
        outputs: Dict[str, str] = {}

        for template in self.task_templates:
            agent = self.agents[template.agent]
            prompt = template.instructions.replace("{structured_json}", payload)
            response = agent.llm.invoke(prompt)
            content = getattr(response, "content", str(response))
            outputs[template.key] = content.strip()

        return outputs
