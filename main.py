"""Streamlit front-end for deterministic blood test analysis."""
from __future__ import annotations

import json
from typing import Any, Dict

import ollama
import streamlit as st
from dotenv import load_dotenv

from extractor import ReportExtractor
from medical_crew import MedicalCrew

load_dotenv()

VISION_MODEL = "llama3.2-vision:11b"
TEXT_MODEL = "qwen2.5vl:32b"


def ensure_ollama_running() -> None:
    try:
        ollama.list()
    except Exception as exc:  # pragma: no cover - UI side effect
        st.error(
            "Unable to communicate with the local Ollama server. "
            f"Ensure {VISION_MODEL} and {TEXT_MODEL} are available.\n{exc}"
        )
        st.stop()


def _display_tests_table(tests: list[Dict[str, Any]]) -> None:
    if not tests:
        st.info("No lab tests were detected. Please verify the upload quality.")
        return
    st.dataframe(tests, use_container_width=True)


def _download_button(data: Dict[str, Any]) -> None:
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button(
        label="Download JSON",
        data=json_bytes,
        file_name="blood_report.json",
        mime="application/json",
    )


def main() -> None:
    ensure_ollama_running()
    st.title("Deterministic Blood Test Intelligence")
    st.caption(
        "Upload a lab report to obtain a structured JSON extraction and"
        " AI-generated explanations based on local Ollama models."
    )

    extractor = ReportExtractor()
    crew = MedicalCrew()

    uploaded_file = st.file_uploader(
        "Upload report (PDF or image)", type=["pdf", "png", "jpg", "jpeg"]
    )

    if not uploaded_file:
        return

    file_bytes = uploaded_file.read()

    if st.button("Analyze Report", type="primary"):
        with st.spinner("Extracting structured data..."):
            try:
                structured = extractor.extract(file_bytes, uploaded_file.name)
            except Exception as exc:
                st.error(f"Extraction failed: {exc}")
                return

        st.subheader("Structured JSON Output")
        st.json(structured)
        _download_button(structured)

        st.subheader("Parsed Lab Tests")
        _display_tests_table(structured.get("tests", []))

        with st.spinner("Generating narrative insights from structured data..."):
            analysis = crew.run(structured)

        st.subheader("AI Narrative Insights")
        st.markdown("### Key Findings")
        st.markdown(analysis.get("key_findings", "No output."))

        st.markdown("### Health Concerns")
        st.markdown(analysis.get("health_concerns", "No output."))

        st.markdown("### Recommended Follow-up Tests")
        st.markdown(analysis.get("recommended_tests", "No output."))

        st.markdown("### Lifestyle Advice")
        st.markdown(analysis.get("lifestyle_advice", "No output."))

        st.markdown("### Trusted Resources")
        st.markdown(analysis.get("trusted_resources", "No output."))


if __name__ == "__main__":
    main()
