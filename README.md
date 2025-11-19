# 🩺 Blood Report Analysis

## Overview

The Medical Report Analysis app is a comprehensive tool designed to analyze blood test reports from PDF files or uploaded images. Built using the Streamlit framework and powered entirely by locally hosted Ollama models (`llama3.2-vision:11b` for vision tasks and `qwen2.5vl:32b` for text reasoning), this application processes the data extracted from the uploaded files and delivers a detailed analysis. Results include key medical findings, potential health concerns, recommended follow-up tests, actionable lifestyle advice, and references to trusted medical resources—all without requiring access to paid external LLM APIs.

## Features

- **Image or PDF Upload:** Users can upload their blood test reports in PDF or image format, which the app will analyze entirely on-device.
- **Detailed Analysis:** The app leverages the CrewAI framework, involving specialized agents, to parse and analyze the report data, providing a comprehensive summary of the results.
- **Health Recommendations:** Based on the analysis, the app generates personalized health advice, including lifestyle modifications and suggested medical follow-ups.
- **Trusted Resources:** The app includes references to high-quality medical articles and resources, allowing users to further understand their health conditions.

## Application Workflow

1. **Data Extraction:** The app uses PyPDF2 to extract text data from the uploaded PDF files.
2. **Analysis:** Leveraging CrewAI, the app processes the data through various agents, each responsible for specific tasks such as summarizing key findings, identifying health concerns, and providing recommendations.
3. **Output:** The processed data is then displayed on the Streamlit interface, categorized into key findings, main health concerns, additional tests or follow-ups, lifestyle advice, and trusted medical resources.

## Installation

### Prerequisites

Ensure that you have Python 3.8 or above installed on your machine along with the latest version of [Ollama](https://ollama.com/).

### Step-by-Step Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AK2k30/BLOOD_TEST_ANALYSIS.git
   ```
   
2. **Install Python Dependencies:**
   Use the following command to install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Ollama Models:**
   Make sure the local Ollama server is running and pull the required models:
   ```bash
   ollama pull llama3.2-vision:11b
   ollama pull qwen2.5vl:32b
   ```

4. **Run the Application:**
   Launch the Streamlit application by running the following command:
   ```bash
   streamlit run main.py
   ```

5. **Access the App:**
   Once the app is running, open the provided URL in your web browser to access the application.

## Usage

1. **Uploading a PDF Report:**
   - Navigate to the app in your web browser.
   - Upload your blood test report using the provided file uploader.
   
2. **Analyzing the Report:**
   - Click the "Analyze Report" button to start the analysis.
   - The app will process the report and provide detailed insights, including:
     - **Summary of Key Findings:** Highlighting the essential observations from the blood test.
     - **Main Health Concerns:** Listing potential health issues based on the test results.
     - **Recommended Additional Tests or Follow-Ups:** Suggesting further medical tests or follow-ups if needed.
     - **Actionable Lifestyle Advice:** Offering advice on lifestyle changes that could improve or maintain your health.
     - **References to Medical Resources:** Providing links to trusted medical articles for further reading.

## Project Structure

```
BLOOD_TEST_ANALYSIS/
│
├── main.py              # Streamlit application entry point (image & PDF analysis)
├── agents.py            # Definitions of CrewAI agents powered by Ollama
├── medical_crew.py      # Object-oriented agent definitions
├── tasks.py             # Task definitions for CrewAI orchestration
├── tools.py             # Search and website retrieval helpers configured for Ollama
├── requirements.txt     # List of Python dependencies
├── pyproject.toml       # Optional Poetry configuration
├── README.md            # Project documentation
└── assets/, db/, etc.   # Supporting assets and data
```

## Contributing

Contributions to the project are welcome! If you have ideas for improvement or new features, please feel free to submit a Pull Request. Before contributing, please ensure that your code adheres to the existing code style and passes all tests.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

