"""Main agent: routes questions to the right DB tool or web search."""

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.llm import get_llm
from tools.db_tools import get_hospitals_tool, get_institutions_tool, get_restaurants_tool
from tools.web_search_tool import get_web_search_tool

SYSTEM_PROMPT = """You are a multi-tool assistant for questions about Bangladesh.

You have 4 tools:
- InstitutionsDBTool: data/statistics questions about schools, colleges, madrasahs
  (counts, locations, management type, education level, etc.)
- HospitalsDBTool: data/statistics questions about DGHS health facilities
  (counts, locations, agency, public/private, etc.)
- RestaurantsDBTool: data/statistics questions about restaurants
  (ratings, reviews, location, name/address search)
- WebSearchTool: general knowledge questions NOT answerable from the 3 databases
  above - definitions, government policy, history, culture, current events.

Routing rules:
1. If the question asks for counts, lists, or specific records from one of the
   3 datasets, call the matching DB tool.
2. If the question is general knowledge (e.g. "What is the healthcare policy of
   Bangladesh?", "What is the role of DGHS?"), call WebSearchTool.
3. If a question could span more than one tool, call each tool you need and
   combine the results into one clear answer.
4. Always answer in clear natural language. Never expose raw SQL or tool
   internals to the user.
"""


def build_agent_executor(verbose: bool = True) -> AgentExecutor:
    llm = get_llm()
    tools = [
        get_institutions_tool(llm),
        get_hospitals_tool(llm),
        get_restaurants_tool(llm),
        get_web_search_tool(),
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose, handle_parsing_errors=True)
