import base64
from io import BytesIO
import os
import tempfile
import time

import ollama
import streamlit as st
from PIL import Image
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

VISION_MODEL = "llama3.2-vision:11b"
TEXT_MODEL = "qwen2.5vl:32b"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def ensure_ollama_running():
    try:
        ollama.list()
    except Exception as exc:
        st.error(
            "Unable to communicate with the local Ollama server. "
            "Please ensure Ollama is installed, running, and that the required models "
            f"({VISION_MODEL} and {TEXT_MODEL}) are pulled.\nDetails: {exc}"
        )
        st.stop()


def _image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _query_ollama(model_name: str, messages: list, content, content_type: str) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            response = ollama.chat(model=model_name, messages=messages)
            return response["message"]["content"].strip()
        except Exception as exc:
            if attempt < MAX_RETRIES - 1:
                st.warning(
                    f"An error occurred. Retrying in {RETRY_DELAY} seconds... "
                    f"(Attempt {attempt + 1}/{MAX_RETRIES})\nDetails: {exc}"
                )
                time.sleep(RETRY_DELAY)
            else:
                st.error(
                    f"Failed to analyze the report after {MAX_RETRIES} attempts.\nDetails: {exc}"
                )
                return fallback_analysis(content, content_type)


def analyze_medical_report(content, content_type):
    prompt = (
        "Analyze this medical report concisely. Provide key findings, diagnoses, "
        "and recommendations using patient-friendly language."
    )

    if content_type == "image":
        encoded_image = _image_to_base64(content)
        messages = [
            {
                "role": "system",
                "content": "You are a medical analysis assistant specialized in interpreting lab reports.",
            },
            {
                "role": "user",
                "content": prompt,
                "images": [encoded_image],
            },
        ]
        return _query_ollama(VISION_MODEL, messages, content, content_type)

    messages = [
        {
            "role": "system",
            "content": "You explain complex blood test findings clearly and safely.",
        },
        {
            "role": "user",
            "content": f"{prompt}\n\n{content}",
        },
    ]
    return _query_ollama(TEXT_MODEL, messages, content, content_type)

def fallback_analysis(content, content_type):
    st.warning("Using fallback analysis method due to API issues.")
    if content_type == "image":
        return "Unable to analyze the image due to API issues. Please try again later or consult a medical professional for accurate interpretation."
    else:  # text
        word_count = len(content.split())
        return f"""
        Fallback Analysis:
        1. Document Type: Text-based medical report
        2. Word Count: Approximately {word_count} words
        3. Content: The document appears to contain medical information, but detailed analysis is unavailable due to technical issues.
        4. Recommendation: Please review the document manually or consult with a healthcare professional for accurate interpretation.
        5. Note: This is a simplified analysis due to temporary unavailability of the AI service. For a comprehensive analysis, please try again later.
        """

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def main():
    ensure_ollama_running()
    st.title("AI-driven Medical Report Analyzer")
    st.write("Upload a medical report (image or PDF) for analysis")

    file_type = st.radio("Select file type:", ("Image", "PDF"))

    if file_type == "Image":
        uploaded_file = st.file_uploader("Choose a medical report image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            image = Image.open(tmp_file_path)
            st.image(image, caption="Uploaded Medical Report", use_column_width=True)

            if st.button("Analyze Image Report"):
                with st.spinner("Analyzing the medical report image..."):
                    analysis = analyze_medical_report(image, "image")
                    st.subheader("Analysis Results:")
                    st.write(analysis)

            os.unlink(tmp_file_path)

    else:  # PDF
        uploaded_file = st.file_uploader("Choose a medical report PDF", type=["pdf"])
        if uploaded_file is not None:
            st.write("PDF uploaded successfully")

            if st.button("Analyze PDF Report"):
                with st.spinner("Analyzing the medical report PDF..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    with open(tmp_file_path, 'rb') as pdf_file:
                        pdf_text = extract_text_from_pdf(pdf_file)

                    analysis = analyze_medical_report(pdf_text, "text")
                    st.subheader("Analysis Results:")
                    st.write(analysis)

                    os.unlink(tmp_file_path)

if __name__ == "__main__":
    main()
