"""General-knowledge web search tool backed by Tavily."""

from langchain_tavily import TavilySearch


def get_web_search_tool():
    return TavilySearch(
        max_results=5,
        name="WebSearchTool",
        description=(
            "Use for general knowledge questions about Bangladesh that are NOT "
            "answerable from the institutions, hospitals, or restaurants databases - "
            "e.g. definitions, government policy, history, culture. Input should be "
            "a plain-English question."
        ),
    )
