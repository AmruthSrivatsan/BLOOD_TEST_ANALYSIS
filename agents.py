"""CrewAI agent definitions that consume structured JSON."""
from __future__ import annotations

from typing import Dict

from crewai import Agent
from langchain_community.chat_models import ChatOllama

from tools import knowledge_base_tool

TEXT_MODEL = "qwen2.5vl:32b"


def _build_llm(temperature: float = 0.1) -> ChatOllama:
    return ChatOllama(model=TEXT_MODEL, temperature=temperature)


def build_agents() -> Dict[str, Agent]:
    """Instantiate all CrewAI agents with JSON-aware prompts."""
    llm = _build_llm()

    blood_test_analyst = Agent(
        role="Blood Test Analyst",
        goal=(
            "Given a structured JSON object with patient details and lab tests, "
            "produce precise key findings backed by the provided numeric values."
        ),
        backstory=(
            "You are a hematologist who only trusts validated data."
            " Work exclusively with the JSON fields provided and avoid inventing"
            " new test results."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    article_researcher = Agent(
        role="Medical Research Specialist",
        goal=(
            "Use the structured lab JSON and known abnormalities to suggest"
            " trusted resources or follow-up readings without inventing values."
        ),
        backstory=(
            "You maintain an offline index of reputable medical societies and"
            " guidelines. Reference concrete lab flags when selecting topics."
        ),
        tools=[knowledge_base_tool],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    health_advisor = Agent(
        role="Holistic Health Advisor",
        goal=(
            "Combine the JSON data and researcher notes to deliver pragmatic"
            " lifestyle advice and recommended follow-up tests."
        ),
        backstory=(
            "You translate quantitative insights into actionable, patient-friendly"
            " plans while clearly noting uncertainties."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    return {
        "analyst": blood_test_analyst,
        "researcher": article_researcher,
        "advisor": health_advisor,
    }
