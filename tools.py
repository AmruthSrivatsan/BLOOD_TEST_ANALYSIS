from crewai_tools import SerperDevTool, WebsiteSearchTool

# Define tools
search_tool = SerperDevTool()

web_search_tool = WebsiteSearchTool(
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="qwen2.5vl:32b",
                temperature=0.7,
            ),
        ),
        embedder=dict(
            provider="ollama",
            config=dict(
                model="qwen2.5vl:32b",
            ),
        ),
    )
)
