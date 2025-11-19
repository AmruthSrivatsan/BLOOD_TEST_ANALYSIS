"""Local helper tools used by CrewAI agents."""
from __future__ import annotations

from typing import List

from crewai_tools import BaseTool


class LocalKnowledgeBaseTool(BaseTool):
    name = "medical_resource_lookup"
    description = (
        "Return relevant links to trusted medical organizations based on a"
        " short query such as 'high cholesterol' or 'anemia'."
    )

    _RESOURCES = {
        "lipid": [
            "American Heart Association - Cholesterol", "https://www.heart.org/en/health-topics/cholesterol",
        ],
        "anemia": [
            "World Health Organization - Anaemia", "https://www.who.int/health-topics/anaemia",
        ],
        "thyroid": [
            "American Thyroid Association", "https://www.thyroid.org/patient-thyroid-information/",
        ],
        "diabetes": [
            "ADA Standards of Care", "https://diabetes.org/diabetes/medication-management",
        ],
    }

    def _run(self, query: str) -> str:
        query_lower = query.lower()
        matched: List[str] = []
        for key, data in self._RESOURCES.items():
            if key in query_lower:
                matched.extend(data)
        if not matched:
            matched.extend([
                "Centers for Disease Control and Prevention - Lab Testing",
                "https://www.cdc.gov/lab/index.html",
            ])
        return "\n".join(matched)

    async def _arun(self, query: str) -> str:
        return self._run(query)


knowledge_base_tool = LocalKnowledgeBaseTool()
